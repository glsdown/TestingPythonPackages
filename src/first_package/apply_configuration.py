import collections.abc
import logging
import pandas as pd
from pydantic import BaseModel, Field, ValidationError, confloat
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .validators import (
    check_column_names,
    check_filestructure,
    check_filedates,
    check_filename,
    check_column,
)


def check_configuration(config):
    """
    Checks the configuration fits the required pattern

    :config: The dictionary configuration
    """

    class TransformationColumnConfiguration(BaseModel):
        function: Callable
        data: List[str]
        functiontype: str
        kwargs: Dict[str, Any]

    class ValidationColumnConfiguration(BaseModel):
        title: str
        functions: List[Callable]
        threshold: confloat(ge=0, le=1)
        mandatory: bool

    class FileNameConfiguration(BaseModel):
        validate_: bool = Field(alias="validate")
        pattern: str

    class FileStructureConfiguration(BaseModel):
        validate_: bool = Field(alias="validate")
        multiple_sheets: bool

    class FileDatesConfiguration(BaseModel):
        validate_: bool = Field(alias="validate")
        data_field: Optional[str]
        min_file_date_regex: Optional[str]
        max_file_date_regex: Optional[str]
        grace_days: Optional[int]

    class CheckHeadingsConfiguration(BaseModel):
        validate_: bool = Field(alias="validate")

    class TransformationConfiguration(BaseModel):
        columns: Dict[
            Union[str, Tuple[str, ...]], List[TransformationColumnConfiguration]
        ]

    class ValidationConfiguration(BaseModel):
        check_filename: FileNameConfiguration
        check_filedates: FileDatesConfiguration
        check_filestructure: FileStructureConfiguration
        check_headings: CheckHeadingsConfiguration
        columns: Dict[Union[str, Tuple[str, ...]], ValidationColumnConfiguration]

    class ConfigurationBase(BaseModel):
        name: str
        validation: ValidationConfiguration
        transformation: TransformationConfiguration

    try:
        config = ConfigurationBase(**config)
        return True
    except ValidationError as e:
        print(e.json())
        return False


def apply_transformation_from_config(config, data):
    """
    Basic application of a python configuration file to a dataframe

    :config: dictionary of the required transformations
    :data: dataframe of data to apply the functions to
    :returns: dataframe of columns as documented in the config
    """

    # Create a new empty dataframe with the same number of rows as the original one
    df = pd.DataFrame(index=data.index)

    # Apply configuration to columns
    for col, meta in config["transformation"]["columns"].items():
        # For each function to be applied
        for operation in meta:
            fn = operation["function"]
            # Check whether the function is to be applied to the source data frame
            if operation["data"] and operation["functiontype"] == "columns":
                result = data.apply(
                    lambda row: fn(
                        *[row[c] for c in operation["data"]], **operation["kwargs"]
                    ),
                    axis=1,
                )
            # If data has been provided but not specified its to be applied to the columns
            # raise an error
            elif operation["data"]:
                raise exception(
                    "Keyword 'data' is only applicable for 'functiontype' of 'columns'"
                )
            elif operation["functiontype"] == "dataframe":
                result = fn(data, **operation["kwargs"])
            # Apply the function using the kwargs only
            else:
                result = fn(**operation["kwargs"])

            # Where the result is to be stored across multiple columns, extract it
            if isinstance(col, tuple):
                for c, r in zip(col, zip(*result)):
                    df[c] = r
            else:
                df[col] = result

    return df


def apply_validation_from_config(config, data, datafilepath):
    """
    Check a file fulfils basic validation criteria

    :config: dictionary of the required validation checks
    :data: dataframe of data to apply the functions to
    :filepath: pathlib.Path object to the original source file
    :returns: True or False on whether file passes the required checks
    """

    # Extract the configuration
    meta = config["validation"]

    # Set a variable to keep track of how the file is doing
    file_pass = True

    # Check whether to check the filename format
    if meta["check_filename"]["validate"]:
        file_pass = file_pass and check_filename(
            datafilepath, meta["check_filename"]["pattern"]
        )

    # Check whether to check the dates in the file match those in the filename
    if meta["check_filedates"]["validate"]:

        file_pass = file_pass and check_filedates(
            meta["check_filedates"],
            data[meta["check_filedates"]["data_field"]],
            f"{datafilepath.stem}",
        )

    # Check whether to check the file structure e.g. multiple sheets etc.
    if meta["check_filestructure"]["validate"]:
        file_pass = file_pass and check_filestructure(
            datafilepath, meta["check_filestructure"]
        )

    # Check whether to check the headings or not
    if meta["check_headings"]["validate"]:

        file_pass = file_pass and check_column_names(
            expected_headings=meta["columns"].keys(), found_headings=data.columns
        )

    # If it's passed up until this point check the individual columns
    if file_pass:
        columns = meta["columns"]

        # Drop empty rows
        data = data.dropna(how="all")

        logging.info("Checking each column statistics.")
        # Check the validity stats of each column
        for col, criteria in columns.items():
            logging.info(f"Checking column {col}...")
            # If it's a mandatory column, and doesn't pass checks, fail it
            if criteria["mandatory"] and not check_column(
                data[criteria["title"]],
                criteria["functions"],
                criteria["threshold"],
            ):
                logging.error(
                    f"{col} did not pass checks, so the file will be rejected."
                )
                file_pass = False

    return file_pass


def update_default_config(default, custom):
    """
    Update a config dictionary with values in a second one

    :default: the default configuration to be updated
    :custom: the overrides to change
    :returns: dictionary with configuration in it
    """

    for k, v in custom.items():
        if isinstance(v, collections.abc.Mapping):
            default[k] = update_default_config(default.get(k, {}), v)
        else:
            default[k] = v
    return default
