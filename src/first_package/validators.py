import datetime
import logging
import pandas as pd
import re

from .reference_data import get_eclass_list
from .utils import get_date, get_date_ddmmyyyy, first_of_month, last_of_month

LIST_ECLASS = get_eclass_list()

# =======================================================================
# Generic error checking
def check_column(data, functions, threshold):
    """
    Function to return a comment on how well populated a data series is
    based on a given threshold and function.

    :data: the pandas dataframe column
    :functions: a list of the functions to apply to check a value is invalid
    :threshold: the threshold of population the column should have
    :returns: dictionary of results
    """

    # Apply the functions to the column to return True/False values
    data = data.map(lambda x: any(f(x) for f in functions)).copy()
    # Identify the number of incorrect values
    data_invalid = data.sum()
    # Identify the number of values in the column
    data_total = data.count()

    if data_total == 0 or data_invalid == data_total:
        # If entire column is invalid or empty
        logging.error("Header supplied, but all data invalid or missing.")
        return False
    else:
        # Find the percentage of invalid values
        data_perc = data_invalid / data_total

        # Check whether the % invalid values is above or below the threshold
        if data_perc > threshold:
            logging.error(f"{data_perc*100 : .2f}% of values are blank or invalid")
            return False

    return True


def check_column_names(expected_headings, found_headings):
    """
    Confirms whether all headings in expected_headings are the same as found_headings

    :expected_headings: a list of headings to be found within the data set
    :found_headings: a list of headings in the data set
    :returns: True if all headings are identical, and False otherwise
    """
    column_missing = False
    column_additional = False

    # Check if column headings exist
    logging.info("Checking column headers are correct.")
    diff_columns = set(expected_headings) - set(found_headings)
    if len(diff_columns) > 0:
        column_missing = True

    # Check whether there are any additional columns (could need renaming)
    extra_columns = set(found_headings) - set(expected_headings)
    if len(extra_columns) > 0:
        column_additional = True

    # Check for duplicate headings
    # NOTE: As mangle_dupe_cols=True, any duplicate columns will be stored in the form column.1.... column.N
    # We use this to avoid overwriting data. However, to identify duplicate original columns, we need to remove
    # these prior to checking for dups
    main_column_names = [i.split(".")[0] for i in found_headings]
    duplicate_headings = len(main_column_names) > len(set(main_column_names))
    if duplicate_headings:
        logging.error("Duplicate headings identified.")
    if column_missing:
        logging.error("Missing headers identified:")
        print(diff_columns)
    if column_additional:
        logging.error("Additional headers identified:")
        print(extra_columns)
    if column_missing or column_additional or duplicate_headings:
        logging.info(
            "File will not pass checks as I am unable to tell "
            "what to do with the columns on my own."
        )
        return False
    return True


def check_filename(filepath, filename_pattern):
    """
    Function to confirm whether a filename is in the correct format.

    :filepath: a pathlib.Path object for the file location
    :filename_pattern: valid regex string to match the filename to
    :returns: dictionary of results
    """

    filename_no_ext = filepath.stem

    # Check whether it's .XLSX or .XLS
    if filepath.suffix[1:].upper() not in ["CSV", "XLSX", "XLS"]:
        logging.error("Not an Excel file.")
        return False
    else:
        # Check the filename fits the pattern
        if re.match(filename_pattern, filename_no_ext):
            return True
    # If it's not in the right format, or filename, then reject it
    return False


def check_filedates(config, data, filename):
    """
    Checks the dates of the file match those within the data frame

    :config: A valid filedate checking configuration dictionary
    :data: a series to do the checks with
    :filename: A string of the filename to extract dates from
    :returns: True if dates are within a grace period, False otherwise
    """

    min_file_date = re.match(config["min_file_date_regex"], filename)
    max_file_date = re.match(config["max_file_date_regex"], filename)

    # Try and convert to date time
    if min_file_date and max_file_date:
        min_file_date = pd.to_datetime(
            min_file_date.groups()[0], errors="coerce", format="%d%m%y", exact=True
        )
        max_file_date = pd.to_datetime(
            max_file_date.groups()[0], errors="coerce", format="%d%m%y", exact=True
        )

        if pd.isna(min_file_date) or pd.isna(max_file_date):
            logging.error("Could not identify dates from filename.")
            return False

        logging.info(
            f"Date range from the filename is {min_file_date.strftime('%d/%m/%Y')} to {max_file_date.strftime('%d/%m/%Y')}"
        )

        # Check data quality
        if min_file_date != first_of_month(
            min_file_date
        ) or max_file_date != last_of_month(max_file_date):
            logging.error("Dates in filename are not first and last of the month.")
            return False
    else:
        logging.error("Could not identify dates from filename.")
        return False

    # Convert the date column to datetime
    data = data.map(get_date)
    # Identify date range in the file
    min_date = data.dropna().min()
    max_date = data.dropna().max()

    if not (min_date and max_date):
        logging.error("Unable to read dates from the date column.")
        return False
    else:
        logging.info(
            f"Date range included in this file is {min_date.strftime('%d/%m/%Y')} to {max_date.strftime('%d/%m/%Y')}"
        )

    # Check whether the intended period matches the file
    grace_days = config["grace_days"]
    if min_date < min_file_date - datetime.timedelta(
        days=grace_days
    ) or max_date > max_file_date + datetime.timedelta(days=grace_days):
        logging.error("File dates outside range in filename.")
        return False

    if min_date < min_file_date or max_date > max_file_date:
        logging.warning("Some dates slightly outside range in filename.")
    logging.info(
        "Dates in the file are within tolerance to dates used in the filename."
    )
    return True


def check_filestructure(filepath, config):
    """
    Check the file structure meets basic requirements

    :filepath: a valid path to the data file
    :config: additional configuration variables
    :returns: True if file passes checks
    """
    # Variable to keep track
    file_pass = True

    # Extract the config requirements
    multiple_sheets = config["multiple_sheets"]

    # Configurable option whether to check for multiple sheets
    if multiple_sheets:

        # Check for multiple sheets
        logging.info("Checking for additional sheets.")
        xl = pd.ExcelFile(filepath)
        sheets = xl.sheet_names

        # If there are multiple sheets, then fail the file if there are more than 1 populated
        if len(sheets) > 1:
            counter = 0
            for sheet in sheets:
                if len(pd.read_excel(xl, sheet_name=sheet)) > 0:
                    counter += 1
            if counter > 1:
                logging.error("Multiple sheets with data found.")
                file_pass = False
            else:
                logging.warning("Multiple sheets found.")

    return file_pass


# =======================================================================
# Specific columns/functions

# Check if empty
def check_empty(cell):
    """
    Returns true if the input is null, false otherwise
    :cell: any value to check
    :returns: True/False
    """
    return pd.isna(cell)


def must_be_valid_date_in_ddmmyyyy(cell):
    """
    Returns true if the input isn't a valid date, false otherwise
    :cell: any value to check
    :returns: True/False
    """
    # Check if it's nan first
    if check_empty(cell):
        return True
    return pd.isna(get_date_ddmmyyyy(cell))


# Check it contains a digit
def must_contain_digit(cell):
    """
    Returns true if the input doesn't contain a digit, false otherwise
    :cell: any value to check
    :returns: True/False
    """
    # Check if it's nan first
    if check_empty(cell):
        return True
    return not bool(re.search("\d", str(cell)))


# Check it contains a letter
def must_contain_letter(cell):
    """
    Returns true if the input doesn't contain a letter, false otherwise
    :cell: any value to check
    :returns: True/False
    """
    # Check if it's nan first
    if check_empty(cell):
        return True
    return not bool(re.search("[a-zA-Z]", str(cell)))


# Check it is numeric
def must_be_numeric(cell):
    """
    Returns true if the input is not numeric, false otherwise
    :cell: any value to check
    :returns: True/False
    """
    # Check if it's nan first
    if check_empty(cell):
        return True
    # If it's not nan, check it's a number
    return pd.isna(pd.to_numeric(str(cell), errors="coerce"))


# Check if it contains alphanumeric, spaces and periods only
def must_be_alphanumeric_space_period(cell):
    """
    Returns true if the input contains anything other than [a-zA-Z .0-9],
    false otherwise
    :cell: any value to check
    :returns: True/False
    """
    # Check if it's nan first
    if check_empty(cell):
        return True
    # If it's not nan, check it's a number
    return not bool(re.match(r"^[a-zA-Z .0-9]+$", str(cell)))


# Check it is numeric and not 0, 1, or 0.01
def not_zero_pound_penny(cell):
    """
    Returns true if the input is not numeric, 0, 1, or 0.01, false otherwise
    :cell: any value to check
    :returns: True/False
    """
    # Check if it's nan first
    if check_empty(cell):
        return True
    # If it's not nan, convert to a number
    cell = pd.to_numeric(str(cell), errors="coerce")
    if check_empty(cell):
        return True
    cell = round(cell, 2)
    # Check it's not 0, 1, or 0.01
    return cell == 0 or cell == 1 or cell == 0.01


# Check it's a number greater than
def must_be_positive(cell):
    """
    Returns true if the input is not a positive numeric value, false otherwise
    :cell: any value to check
    :returns: True/False
    """
    cell = pd.to_numeric(str(cell), errors="coerce")
    if check_empty(cell):
        return True
    return cell <= 0


# Checks TOTAL
def check_total(price, qty, total):
    """
    Returns the difference between total and price * qty
    :price: the price to check
    :qty: the qty to check
    :total: the total to verify that price * qty = total
    :returns: the absolute difference between price * qty and total
    """
    # Convert the values to numbers
    price = pd.to_numeric(price, errors="coerce")
    qty = pd.to_numeric(qty, errors="coerce")
    total = pd.to_numeric(total, errors="coerce")
    # Get the difference in calculated total and actual total
    if price and qty and total:
        return round(abs(total - (price * qty)), 2)
    return 0


# Checks eCLASS
def check_eclass(eclass):
    """
    Returns true if the input is not a valid eclass, false otherwise
    :cell: any value to check
    :returns: True/False
    """
    eclass = str(eclass)
    # Should be a valid eclass
    return eclass not in LIST_ECLASS


# Find only digits & periods
def contains_only_digit_period(cell):
    """
    Returns true if the input contains values other than numbers and
    periods, false otherwise
    :cell: any value to check
    :returns: True/False
    """
    # Check if empty
    if check_empty(cell):
        return True
    return not bool(re.match("^[\d\.]+$", str(cell)))
