from first_package import remove_vat

custom_config = {
    "name": "custom",
    "transformation": {
        "columns": {
            "price": [
                {
                    "function": remove_vat,
                    "data": ["price"],
                    "functiontype": "columns",
                    "kwargs": {},
                }
            ],
        }
    },
}
