import pandas as pd


def apply_pipeline_from_config(config, filetype, data):
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
    for col, meta in config[filetype]["columns"].items():
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
