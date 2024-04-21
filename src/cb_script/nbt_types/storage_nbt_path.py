class storage_nbt_path:
    def __init__(self, target: str | None, path: str) -> None:
        self.target = target
        self.path = path

    def get_target(self, func) -> str:
        if self.target == None:
            return func.namespace
        else:
            return self.target

    def get_dest_path(self, func) -> str:
        return f"storage {self.get_target(func)} {self.path}"

    def get_source_path(self, func) -> str:
        return "from " + self.get_dest_path(func)
