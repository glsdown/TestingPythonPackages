import pandas as pd

from first_package import apply_transformation_from_config
import configuration

if __name__ == "__main__":

    df = pd.read_csv("data.csv")

    print(apply_transformation_from_config(configuration.config, "test", df))
