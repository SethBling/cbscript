class mock_selector_definition(object):
    def __init__(self):
        self.scores_min = {}
        self.scores_max = {}
        self.parts = {}
        self.paths = {}
        self.vector_paths = {}
        self.is_single_entity = False
        self.type = None
        self.tag = ""

    def set_part(self, part, val):
        self.parts[part] = val

    def single_entity(self):
        return self.is_single_entity

    def get_type(self):
        return self.type
