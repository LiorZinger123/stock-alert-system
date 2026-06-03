from typing import Any


def round_price_helper(v: Any) -> Any | float:
    if v is None:
        return v
    return round(float(v), 2)
