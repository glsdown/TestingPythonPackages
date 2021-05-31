import pandas as pd

from first_package import (
    apply_transformation_from_config,
    update_default_config,
    check_configuration,
)
from configuration import default_config
from custom_configuration import custom_config

if __name__ == "__main__":

    # Read in the data
    df = pd.read_csv("data.csv")

    # Identify any additional configurations required
    config = update_default_config(default_config, custom_config)

    check_configuration(config)

    # Display the result
    print(apply_transformation_from_config(config, df))
