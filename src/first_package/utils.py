import datetime
import logging
import pandas as pd
import shutil

# Function to extract a date from a string
def get_date(value):
    # If it's already a datetime, then return that
    if isinstance(value, datetime.datetime):
        return value
    # If it's a null value, then return that
    if pd.isna(value):
        return np.nan
    # Otherwise try to convert it using lots of formats
    for date_format in ["%d/%m/%Y", "%Y-%m-%d", "%d%m%Y", "%d%m%y"]:
        value_as_date = pd.to_datetime(
            value, errors="coerce", format=date_format, exact=True
        )
        # If it could be converted, then return the value
        if not pd.isna(value_as_date):
            return value_as_date
    # If none of the known formats work, then try inferring it
    return pd.to_datetime(
        value,
        errors="coerce",
        dayfirst=True,
        exact=True,
        infer_datetime_format=True,
    )


# Function to extract a date from a string
def get_date_ddmmyyyy(value):
    """
    Converts a value to a valid datetime object when it's in the form dd/mm/yyyy,
    or nan if it cannot identify a date from the string.
    :value: the string to convert to datetime
    :returns: True/False
    """
    # If it's already a datetime, then return that
    if isinstance(value, datetime.datetime):
        return value
    # If it's a null value, then return that
    if pd.isna(value):
        return np.nan
    # Try to convert using the required format
    return pd.to_datetime(
        value,
        errors="coerce",
        format="%d/%m/%Y",
        exact=True,
        infer_datetime_format=False,
    )


# Function to identify the last day in a month
def last_of_month(value):
    """
    Converts a datetime object to the last day of the month
    :value: the datetime to get the last day of the month from
    :returns: datetime of the last day of the month
    """
    return datetime.date(
        value.year + value.month // 12, value.month % 12 + 1, 1
    ) - datetime.timedelta(1)


# Function to identify the first day in a month
def first_of_month(value):
    """
    Converts a datetime object to the first day of the month
    :value: the datetime to get the first day of the month from
    :returns: datetime of the first day of the month
    """
    return value.replace(day=1)


# Function to copy a file
def copy_file(src, dest):
    """
    Copies a file from the src to dest folders.
    :src: the source file
    :dest: the destination folder
    """
    try:
        shutil.copy(src, dest)
    # eg. src and dest are the same file
    except shutil.Error as e:
        logging.exception("Error: %s" % e)
    # eg. source or destination doesn't exist
    except IOError as e:
        logging.exception("Error: %s" % e.strerror)
