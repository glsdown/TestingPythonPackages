import numpy as np
import pandas as pd
import re


def strip_whitespace(value):
    """
    Strips any whitespace from the start or end of the value

    :value: any value to strip from
    :returns: string or None
    """
    # Check if it's null already
    if pd.isna(value):
        return None
    # Return the stripped string
    return str(value).strip()


def calculate_total(price, qty):
    """
    Calculates price x qty

    :price: float
    :qty: float
    :returns: float or None
    """
    # Check for blanks
    if pd.isna(price) or pd.isna(qty):
        return None
    try:
        price = float(price)
        qty = float(qty)
        return price * qty
    except:
        return None


def remove_vat(value, rate=0.2):
    """
    Remove vat from a value

    :value: the value to remove VAT from
    :returns: float or None
    """
    # Check for blanks
    if pd.isna(value):
        return None
    # Convert to numeric
    value = get_numeric(value)
    if pd.isna(value):
        return None
    # Remove the vat
    return value / (1 + rate)


def identify_uom(uom):
    """
    Identifies the UOM value and description given a string input
    of the UOM.

    :uom: The string value to extract from
    :returns: tuple of uom_value (float), uom_desc (string) or None, None
    """
    # Check for blanks
    if pd.isna(uom):
        return None, None
    uom = str(uom)
    # Check for common values
    if uom.lower() == "each":
        return 1, "Each"
    elif uom.lower() == "pair":
        return 2, "Box"
    # Search for numbers
    nums = re.compile(r"^\d+(?:\.\d+)?$")
    numbers = [float(i) for i in uom.split() if nums.match(i)]
    # if a number could be found, use that
    if numbers:
        uom_value = numbers[0]
        if uom_value == 1:
            return 1, "Each"
        return uom_value, "Box"
    # If a number couldn't be found return None, None
    return None, None


def get_numeric(value, decimal_place=None):
    """
    Converts the value to a numeric value

    :value: string containing the number to convert
    :decimal_place: (optional) number of places to round to
    """
    # Check if it's null
    if pd.isna(value):
        return np.nan
    # Convert to a number
    value = pd.to_numeric(str(value).strip(), errors="coerce")
    # If it can't convert it, return nan
    if pd.isna(value):
        return np.nan
    # If there is a request to round it, then do that
    if pd.isna(decimal_place):
        return value
    return round(value, decimal_place)


def get_row_number(df):
    """
    Returns a Series object with the row number on each line

    :df: The dataframe to create the series for
    :returns: Series
    """
    return np.arange(df.shape[0]) + 1
