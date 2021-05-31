from dagster import pipeline
from solids import log_dataframe, rename_columns, read_data


@pipeline
def rename_test():
    log_dataframe(rename_columns(read_data()))
