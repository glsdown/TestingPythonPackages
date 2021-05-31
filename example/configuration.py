import datetime
from first_package import (
    # validators
    check_empty,
    must_be_valid_date_in_ddmmyyyy,
    must_contain_digit,
    must_contain_letter,
    must_be_numeric,
    must_be_alphanumeric_space_period,
    not_zero_pound_penny,
    must_be_positive,
    check_eclass,
    contains_only_digit_period,
    # transformation
    calculate_total,
    strip_whitespace,
    identify_uom,
    get_numeric,
    get_row_number,
)

default_config = {
    "name": "default",
    "filetype": "test",
    "validation": {
        "check_filename": {
            "validate": True,
            "pattern": r"^[a-zA-Z0-9]{3}_01[0-9]{4}_[0-9]{6}",
        },
        "check_filedates": {
            "validate": True,
            "data_field": "DATE",
            "min_file_date_regex": r"^[a-zA-Z]{3}_([0-9]{6})_[0-9]{6}$",
            "max_file_date_regex": r"^[a-zA-Z]{3}_[0-9]{6}_([0-9]{6})$",
            "grace_days": 10,
        },
        "check_filestructure": {"validate": True, "multiple_sheets": False},
        "check_headings": {"validate": True},
        "columns": {
            "DATE": {
                "title": "DATE",
                "functions": [must_be_valid_date_in_ddmmyyyy],
                "threshold": 0,
                "mandatory": True,
            },
            "PONUM": {
                "title": "PONUM",
                "functions": [must_contain_digit],
                "threshold": 0.05,
                "mandatory": False,
            },
            "SUPPLIER": {
                "title": "SUPPLIER",
                "functions": [must_contain_letter],
                "threshold": 0.20,
                "mandatory": True,
            },
            "MPC": {
                "title": "MPC",
                "functions": [must_contain_digit],
                "threshold": 0.10,
                "mandatory": True,
            },
            "DESC": {
                "title": "DESC",
                "functions": [check_empty],
                "threshold": 0.20,
                "mandatory": False,
            },
            "PRICE": {
                "title": "PRICE",
                "functions": [must_be_numeric, not_zero_pound_penny],
                "threshold": 0.15,
                "mandatory": True,
            },
            "QTY": {
                "title": "QTY",
                "functions": [must_be_positive],
                "threshold": 0.15,
                "mandatory": True,
            },
            "TOTAL": {
                "title": "TOTAL",
                "functions": [must_be_numeric],
                "threshold": 0.1,
                "mandatory": True,
                "variance_threshold": 500000,
            },
            "UOM": {
                "title": "UOM",
                "functions": [must_be_alphanumeric_space_period],
                "threshold": 0.20,
                "mandatory": True,
            },
            "POLINE": {
                "title": "POLINE",
                "functions": [contains_only_digit_period],
                "threshold": 0.15,
                "mandatory": False,
            },
            "eCLASS": {
                "title": "eCLASS",
                "functions": [check_eclass],
                "threshold": 0.15,
                "mandatory": False,
            },
            "COSTCENTRE": {
                "title": "COSTCENTRE",
                "functions": [check_empty],
                "threshold": 0.15,
                "mandatory": False,
            },
            "CONTRACTREF": {
                "title": "CONTRACTREF",
                "functions": [check_empty],
                "threshold": 0.15,
                "mandatory": False,
            },
        },
    },
    "transformation": {
        "columns": {
            "price": [
                {
                    "function": get_numeric,
                    "data": ["price"],
                    "functiontype": "columns",
                    "kwargs": {"decimal_place": 2},
                }
            ],
            "qty": [
                {
                    "function": get_numeric,
                    "data": ["qty"],
                    "functiontype": "columns",
                    "kwargs": {"decimal_place": 1},
                }
            ],
            "total": [
                {
                    "function": calculate_total,
                    "data": ["price", "qty"],
                    "functiontype": "columns",
                    "kwargs": {},
                }
            ],
            "code": [
                {
                    "function": strip_whitespace,
                    "data": ["code"],
                    "functiontype": "columns",
                    "kwargs": {},
                }
            ],
            ("uom_value", "uom_desc"): [
                {
                    "function": identify_uom,
                    "data": ["uom"],
                    "functiontype": "columns",
                    "kwargs": {},
                }
            ],
            "date": [
                {
                    "function": datetime.datetime.today().date,
                    "data": [],
                    "functiontype": "constant",
                    "kwargs": {},
                }
            ],
            "row": [
                {
                    "function": get_row_number,
                    "data": [],
                    "functiontype": "dataframe",
                    "kwargs": {},
                }
            ],
        }
    },
}
