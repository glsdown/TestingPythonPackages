from dagster import pipeline
from solids import (
    add_row_number,
    calculate_total,
    identify_uom,
    log_dataframe,
    get_numeric,
    read_data,
    strip_whitespace,
)


@pipeline
def simple_pipeline():
    steps = [
        get_numeric,
        calculate_total,
        strip_whitespace,
        identify_uom,
        add_row_number,
    ]

    df = read_data()

    for step in steps:
        df = step(df)

    log_dataframe(df)
