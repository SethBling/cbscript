class block_nbt_path:
    def __init__(self, coords, path):
        self.coords = coords
        self.path = path

    def get_dest_path(self, func) -> str:
        return f"block {self.coords.get_value(func)} {self.path}"

    def get_source_path(self, func) -> str:
        return "from " + self.get_dest_path(func)
