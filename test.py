#!pytest

import tableplotter

def test__truncated_table():
    assert tableplotter._truncated_table(
            table=[
                [ "row_keys", "col_1", "col_2", "col_3" ],
                [ "foo", 1, 2, 3 ],
                [ "bar", 4, 5, 6 ],
                [ "baz", 7, 8, 9 ],
                ],
            row_keys=[ "foo", "bar" ],
            num_recent_columns=2
            ) == [
                [ "row_keys", "col_2", "col_3" ],
                [ "foo", 2, 3 ],
                [ "bar", 5, 6 ],
                ]

    assert tableplotter._truncated_table(
            table=[
                [ "row_keys", "col_1", "col_2", "col_3" ],
                [ "foo", 1, 2, 3 ],
                [ "bar", 4, 5, 6 ],
                [ "baz", 7, 8, 9 ],
                ],
            row_keys=None,
            num_recent_columns=None
            ) == [
                [ "row_keys", "col_1", "col_2", "col_3" ],
                [ "foo", 1, 2, 3 ],
                [ "bar", 4, 5, 6 ],
                [ "baz", 7, 8, 9 ],
                ]
def test__sorted_figdata():
    assert tableplotter._sorted_figdata(
            name_to_scale={ "foo": 1.0, "bar": 2.0, "baz": 3.0 },
            name_to_values={ "foo" : [ 1, 2, 3 ], "bar" : [ 4, 5, 6 ], "qux": [ 7, 8, 9 ] },
            ) == [
                    {
                        "name": "bar",
                        "yvalues": [ 2.0, 2.5, 3.0 ],
                        "linestyle": "-",
                        },
                    {
                        "name": "foo",
                        "yvalues": [ 1.0, 2.0, 3.0 ],
                        "linestyle": "-",
                        }
                    ]

def test__name_to_scale():
    json = {
            "foo": {
                "key_1": 1.0,
                "key_2": 2.0,
                },
            "bar": {
                "key_1": 1.0,
                "key_2": 2.0,
                "key_3": 3.0,
                },
            "baz": {
                "key_1": 1.0,
                "key_2": 2.0,
                "key_3": 3.0,
                }
            }

    assert tableplotter._name_to_scale(
            json=json,
            select_names=[ "foo", "bar" ],
            scale_key="key_2",
            scale_factor=2.0
            ) == {
                    "foo": 4.0,
                    "bar": 4.0,
                    }

    assert tableplotter._name_to_scale(
            json=json,
            select_names=None,
            scale_key="key_2",
            scale_factor=2.0
            ) == {
                    "foo": 4.0,
                    "bar": 4.0,
                    "baz": 4.0,
                    }

    assert tableplotter._name_to_scale(
            json=json,
            select_names=None,
            scale_key="key_3",
            scale_factor=2.0
            ) == {
                    "bar": 6.0,
                    "baz": 6.0,
                    }

    assert tableplotter._name_to_scale(
            json=json,
            select_names=[ "foo", "bar" ],
            scale_key=None,
            scale_factor=2.0
            ) == {
                    "foo": 2.0,
                    "bar": 2.0,
                    }

    assert tableplotter._name_to_scale(
            json=json,
            select_names=None,
            scale_key=None,
            scale_factor=2.0
            ) == {
                    "foo": 2.0,
                    "bar": 2.0,
                    "baz": 2.0,
                    }

