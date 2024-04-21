class entity_nbt_path:
    def __init__(self, selector: str, path: str) -> None:
        self.selector = selector
        self.path = path

    def get_dest_path(self, func) -> str:
        return f"entity {self.selector} {self.path}"

    def get_source_path(self, func) -> str:
        return "from " + self.get_dest_path(func)
