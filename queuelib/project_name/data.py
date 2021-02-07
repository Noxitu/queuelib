import os


class dataset:
    def __init__(self, path, *, require_xyz=False):
        self.path = path
        self.name = os.path.split(path)[-1]
        self.title = f'Dataset {self.name}'
        self._require_xyz = require_xyz

    def verify(self):
        return True and not self._require_xyz


class summary:
    def __init__(self, path, name):
        self.path = path
        self.title = f'Summary for {name}'

    def verify(self):
        return False
