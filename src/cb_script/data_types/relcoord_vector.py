from cb_script.CompileError import CompileError


class relcoord_vector:
    def __init__(self, line, type, value):
        self.type = type
        self.value = value
        self.line = line

    def get_value(self, func):
        coords = self.value.get_value(func)
        relcoords = []
        try:
            for i in range(3):
                relcoords.append(f"{self.type}{coords[i]}")
        except Exception as e:
            raise CompileError(
                f"Unable to get three coordinates from constant value at line {self.line}."
            )

        return " ".join(relcoords)
