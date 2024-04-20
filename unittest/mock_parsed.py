class mock_parsed(object):
    def __init__(self, *args):
        self.p = [None] + list(args)

    def __getitem__(self, key):
        return self.p[key]

    def __setitem__(self, key, value):
        self.p[key] = value

    def lineno(self, key):
        return 0

    def __len__(self):
        return len(self.p)
