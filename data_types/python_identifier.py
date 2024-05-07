class python_identifier(object):
    def __init__(self, id, negate=False):
        self.id = id
        self.negate = negate

    def get_value(self, func):
        if self.negate:
            return -func.get_dollarid(self.id)
        else:
            return func.get_dollarid(self.id)
