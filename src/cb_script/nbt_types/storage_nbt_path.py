class storage_nbt_path(object):
    def __init__(self, target, path):
        self.target = target
        self.path = path

    def get_target(self, func):
        if self.target == None:
            return func.namespace
        else:
            return self.target

    def get_dest_path(self, func):
        return f"storage {self.get_target(func)} {self.path}"

    def get_source_path(self, func):
        return "from " + self.get_dest_path(func)
