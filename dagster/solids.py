import first_package
import numpy as np
import pandas as pd
from dagster import Any, Array, Field, solid


@solid(config_schema={"data_path": str})
def read_data(context):
    path = context.solid_config["data_path"]
    df = pd.read_csv(path)
    context.log.info(f"Loading file: {context.solid_config['data_path']}")
    context.log.info(f"Data has {df.shape[0]} rows")
    return df


@solid(config_schema={"column_name": Field(str, default_value="row")})
def add_row_number(context, df):
    df[context.solid_config["column_name"]] = np.arange(df.shape[0]) + 1
    return df


@solid(config_schema={"column_name": Field(str, default_value="total")})
def calculate_total(context, df):
    df[context.solid_config["column_name"]] = df["price"] * df["qty"]
    return df


@solid(
    config_schema={
        "decimal_place": Field(int, default_value=2),
        "columns": Field(Array(str)),
    }
)
def get_numeric(context, df):
    cols = context.solid_config.get("columns", [])
    for col in cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        ).round(decimals=context.solid_config["decimal_place"])
    return df


@solid(
    config_schema={
        "column_names": Field(
            Array(str), default_value=["uom_value", "uom_desc"]
        )
    }
)
def identify_uom(context, df):
    cols = context.solid_config["column_names"]
    result = df.apply(lambda row: first_package.identify_uom(row.uom), axis=1)
    for c, r in zip(cols, zip(*result)):
        df[c] = r
    return df


@solid
def log_dataframe(context, df):
    context.log.info(df.to_markdown(index=False))


@solid(
    config_schema={
        "rate": Field(float, default_value=0.2),
        "column_name": Field(str, default_value="total_pre_vat"),
    }
)
def remove_vat(context, df):
    df[context.solid_config["column_name"]] = df.apply(
        lambda row: first_package.remove_vat(
            row.total, rate=context.solid_config["rate"]
        ),
        axis=1,
    )
    return df


@solid(config_schema={"columns": Field(Array(str))})
def strip_whitespace(context, df):
    cols = context.solid_config.get("columns", [])

    for col in cols:
        if pd.api.types.infer_dtype(df[col]) == "string":
            df[col] = df[col].str.strip()

    return df


@solid(config_schema={"columns": Field(dict, default_value={})})
def rename_columns(context, df):
    columns = context.solid_config["columns"]
    if columns:
        return df.rename(columns=columns)
    return df
