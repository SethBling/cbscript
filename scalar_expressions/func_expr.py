from .scalar_expression_base import scalar_expression_base
from variable_types.scoreboard_var import scoreboard_var
from environment import isInt
import math


def factor(n):
    i = 2
    limit = math.sqrt(n)
    while i <= limit:
        if n % i == 0:
            yield i
            n = n // i  # Use integer division for Python 3
            limit = math.sqrt(n)
        else:
            i += 1
    if n > 1:
        yield n


class func_expr(scalar_expression_base):
    def __init__(self, function_call):
        self.function_call = function_call

    def compile(self, func, assignto=None):
        self.function_call.compile(func)

        return scoreboard_var("Global", "ReturnValue")
