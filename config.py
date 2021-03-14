import json
import os


default_config = {
    "lnkFiles": [],
    "shortcut": ["control", "q"]
}


class Config(dict):
    def __init__(self, path='config.json'):
        super(Config, self).__init__()
        self.path = path
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.update(data)
        else:
            self.update(default_config)
            self.flush()

    def __setitem__(self, key, value):
        super(Config, self).__setitem__(key, value)

    def flush(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self, f, ensure_ascii=False, indent=4)

    def is_lnk_exists(self, lnk_path):
        try:
            self['lnkFiles'].index(lnk_path)
            return True
        except ValueError:
            return False

    def remove_lnk(self, lnk_path):
        try:
            self['lnkFiles'].remove(lnk_path)
        except ValueError:
            pass
