class nbt_json:
    def __init__(self, json):
        self.json = json

    def get_source_path(self, func):
        return f"value {self.json}"
