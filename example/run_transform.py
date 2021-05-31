import logging
import pandas as pd
from pathlib import Path

from first_package import (
    apply_validation_from_config,
    apply_transformation_from_config,
    update_default_config,
    check_configuration,
)
from configuration import default_config
from custom_configuration import custom_config

if __name__ == "__main__":

    # Set up the logger
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        level=logging.INFO,
    )

    datafilepath = Path("XXX_010521_310521.csv")  # Path("data.csv")

    # Read in the data
    df = pd.read_csv(datafilepath, mangle_dupe_cols=True)

    # Identify any additional configurations required
    config = update_default_config(default_config, custom_config)

    # Check the config file is the right format
    if check_configuration(config):
        # Check file is valid
        if apply_validation_from_config(config, df, datafilepath):
            # Display the result
            print("pass")
            # print(apply_transformation_from_config(config, df))
    else:
        print("Ill formed configuration file")
