# tableplotter

Wrapper around Matplotlib for plotting table-shaped data.

This tool allows easy plotting of CSV tables with a header row and a first column containing the labels for contiguous data points.

The subset of rows to be plotted is controlled by a JSON configuration file.
This file also contains scaling factors for the data points.

## Tested requirements

- OS: Raspbian Buster
- GNU bash 5.0.3(1)
- GNU Make 4.2.1
- Git 2.20.1
- Python 3.7.3
    - matplotlib 3

## Installation

```
git clone <repository url>
cd <repository url>
make dependencies
```

## Usage

```
./tableplotter.py -h
```
