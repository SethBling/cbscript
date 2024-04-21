class entity_nbt_path:
    def __init__(self, selector, path):
        self.selector = selector
        self.path = path

    def get_dest_path(self, func):
        return f"entity {self.selector} {self.path}"

    def get_source_path(self, func):
        return "from " + self.get_dest_path(func)
