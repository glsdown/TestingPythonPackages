import datetime
from first_package import (
    calculate_total,
    strip_whitespace,
    identify_uom,
    get_numeric,
    get_row_number,
)

default_config = {
    "name": "default",
    "test": {
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
