#!/usr/bin/env python3

import os
import re
import csv
import sys
import json
import math
import argparse

import numpy as np
import matplotlib.pyplot as plt

def _positive_integer(x):
    i = int(x)
    if i > 0:
        return i
    else:
        raise argparse.ArgumentTypeError("Positive integer value required: {}".format(x))

def _non_zero_float(x):
    f  = float(x)
    if f != 0.0:
        return f
    else:
        raise argparse.ArgumentTypeError("Non-zero float value required: {}".format(x))

def _positive_integer_tuple(x):
    if re.search("^\\d+,\\d+$", x):
        return tuple([int(x) for x in x.split(",")])
    else:
        raise argparse.ArgumentTypeError("Comma-separated tuple of positive integers required: {}".format(x))

def _args():
    parser = argparse.ArgumentParser(description='Plot data from CSV files.')

    parser.add_argument("--input", "-i", type=str, action="store", required=True,
            help="Input paths to CSV files.")

    parser.add_argument("--output", "-o", type=str, action="store", required=True,
            help="Output path to PNG file")

    parser.add_argument("--scale-map", "-m", type=str, action="store", required=True,
            help="Path to scale map mapping plot keys to scale factors (JSON format: { <row_key>: { <scale_key>: <value>, ... }, ... })")

    parser.add_argument("--scale-key", "-k", type=str, action="store", default=None,
            help="Key to scale factors to be used, as defined in scale map")

    parser.add_argument("--scale-factor", "-p", action="store", default=1.0,
            type=_non_zero_float,
            help="Precision factor applied to scale (use it to avoid precision errors when scaling large y values)")

    parser.add_argument("--num-recent-columns", "-r", action="store", default=None,
            type=_positive_integer,
            help="Number of recent columns to plot (default: all)")

    parser.add_argument("--names", "-n", nargs="+", type=str, action="store", default=None,
            help="Keys of rows to plot (default: all)")

    # Matplotlib options

    parser.add_argument("--title", "-t", type=str, action="store", default="",
            help="Title option passed to Matplotlib")

    parser.add_argument("--figsize", "-s", action="store", default="15,15",
            type=_positive_integer_tuple,
            help="Figsize option passed to Matplotlib, as comma-separated tupel of positive integers")

    parser.add_argument("--dpi", "-d", type=int, action="store", default=80,
            help="DPI option passed to Matplotlib")

    parser.add_argument("--xlabel", "-x", type=str, action="store", default="",
            help="Xlabel option passed to Matplotlib")

    parser.add_argument("--ylabel", "-y", type=str, action="store", default="",
            help="Ylabel option passed to Matplotlib")

    parser.add_argument("--yscale", "-f", type=str, action="store", default=None,
            help="Yscale option passed to Matplotlib")

    return parser.parse_args()

def _truncated_table(table, row_keys, num_recent_columns):
    xvalue_begin=(
            lambda x: x - (num_recent_columns is None and x or num_recent_columns)
            )(len(table[0])-1)

    assert xvalue_begin >= 0, "Value of --num-recent-columns ({}) must be <= {} for this data.".format(num_recent_columns, len(table[0])-1)

    return [
            [row[0]] + row[1+xvalue_begin:]
            for idx, row in enumerate(table)
            if
                idx == 0
                or row_keys is None
                or row[0] in row_keys
            ]

def _name_to_scale(json, names, scale_key, scale_factor):
    return {
            name: (
                scale_key is None
                    and 1.0
                or scale_key_to_scale[scale_key]
                ) * scale_factor
            for name, scale_key_to_scale in json.items()
            if
                (
                    names is None
                    or name in names
                    )
                    and (
                        scale_key is None
                        or scale_key in scale_key_to_scale
                        )
            }

def _define_xaxis(ax, xticks, xticklabels, xlabel):
    ax.set_xlabel(xlabel)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.tick_params(axis="x", labelrotation=-60)

def _define_yaxis(ax, min_yvalue, max_yvalue, ysize, yscale, ylabel):
    if yscale is not None:
        ax.set_yscale(yscale)
    else:
        ax.set_yticks(
                np.arange(
                    min_yvalue,
                    max_yvalue,
                    step=(lambda x: round(x, -(len(str(x))-1)))(round(max_yvalue / (ysize * 2)))
                    )
                )

        ax.set_ylim(min_yvalue, max_yvalue)

    ax.set_ylabel(ylabel)
    ax.tick_params(right=True, labelright=True)

def _sorted_entries(name_to_scale, name_to_values, names):
    return [
            {
                "name": name,
                "yvalues": [
                    value / name_to_scale[name]
                    for value in name_to_values[name]
                    ],
                "linestyle": len(name.split("/")) > 1 and ":" or "-"
                }
            for name in sorted(names)
            ]

def _plot(ax, entries):
    for entry in entries:
        ax.plot(
                entry["yvalues"],
                label=entry["name"],
                linestyle=entry["linestyle"]
                )

def _main(args):
    plt.set_cmap("hsv")

    _, ax = plt.subplots(
            figsize=args.figsize,
            dpi=args.dpi
            )

    with open(args.scale_map, "r") as jsonfile:
        name_to_scale = _name_to_scale(
                json.load(jsonfile),
                args.names,
                args.scale_key,
                args.scale_factor
                )

    if args.names is None:
        names = set(name_to_scale.keys())
    else:
        names = set(name_to_scale.keys()).intersection(set(args.names))

    with open(args.input, "r") as csvfile:
        table = _truncated_table(
                list(csv.reader(csvfile, delimiter=',')),
                names,
                args.num_recent_columns
                )

    name_to_values = {
            row[0]: [ float(n) for n in row[1:] ]
            for row in table[1:]
            }

    entries = _sorted_entries(
            name_to_values=name_to_values,
            name_to_scale=name_to_scale,
            names=sorted(names.intersection(set(name_to_values.keys())))
            )

    _plot(
            ax,
            entries=entries
            )

    _define_xaxis(
            ax,
            xticks=np.arange(0, len(table[0][1:])),
            xticklabels=table[0][1:],
            xlabel=args.xlabel
            )

    all_yvalues = [ x for entry in entries for x in entry["yvalues"] ]

    _define_yaxis(
            ax,
            min_yvalue=(lambda x: 0.0 if args.yscale is None and x > 0.0 else x)(min(all_yvalues)),
            max_yvalue=max(all_yvalues),
            ysize=args.figsize[1],
            yscale=args.yscale,
            ylabel="".join([
                (args.yscale is not None and args.yscale + "(" or ""),
                args.ylabel,
                (args.scale_key is not None and " / " or ""),
                (args.scale_factor != 1.0 and " (" or ""),
                (args.scale_key is not None and args.scale_key or ""),
                (args.scale_factor != 1.0 and " * " + str(args.scale_factor) + ")" or ""),
                (args.yscale is not None and ")" or ""),
                ])
            )

    ax.grid(
            axis="x",
            color="black",
            alpha=.3,
            linewidth=.5,
            linestyle="-",
            )

    ax.grid(
            axis="y",
            color="black",
            alpha=.5,
            linewidth=.5,
            linestyle="-",
            )

    ax.set_title(args.title)

    plt.legend()

    plt.savefig(args.output)

if __name__ == "__main__":
    _main(_args())
