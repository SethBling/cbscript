from typing import NamedTuple


class const_string(NamedTuple):
    val: str

    def get_value(self, func) -> str:
        return self.val
