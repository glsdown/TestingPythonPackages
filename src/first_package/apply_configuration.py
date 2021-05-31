import collections.abc
import pandas as pd
from pydantic import BaseModel, ValidationError
from typing import Any, Callable, Dict, List


def check_configuration(config):
    """
    Checks the configuration fits the required pattern

    :config: The dictionary configuration
    """

    class ColumnConfiguration(BaseModel):
        function: Callable
        data: List[str]
        functiontype: str
        kwargs: Dict[str, Any]

    class TransformationConfiguration(BaseModel):
        columns: Dict[str, List[ColumnConfiguration]]

    class ConfigurationBase(BaseModel):
        name: str
        transformation: TransformationConfiguration

    try:
        config = ConfigurationBase(config)
    except ValidationError as e:
        print(e.json())


def apply_transformation_from_config(config, data):
    """
    Basic application of a python configuration file to a dataframe

    :config: dictionary of the required transformations
    :filetype: string, the type of file being processed
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
