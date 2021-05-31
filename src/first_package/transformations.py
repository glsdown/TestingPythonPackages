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
