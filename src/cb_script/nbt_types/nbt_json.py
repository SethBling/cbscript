class nbt_json:
    def __init__(self, json: str) -> None:
        self.json = json

    def get_source_path(self, func) -> str:
        return f"value {self.json}"
