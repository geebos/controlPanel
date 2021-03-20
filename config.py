import json
import os


class FilesPath:
    image_auto_start_green = 'icons/auto_start_green.png'
    image_auto_start_gray = 'icons/auto_start_gray.png'

    image_exit = 'icons/exit.png'
    image_logo = 'icons/logo.png'

    image_add_lnk = 'icons/add.png'
    image_delete_lnk = 'icons/delete.png'


class StringsList:
    auto_start_open = '设置开机自启动'
    auto_start_close = '关闭开机自启动'

    exit = '退出'
    hint = '提示'

    select_lnk = '选择快捷方式'
    add_lnk = '添加'
    delete_lnk = '删除'
    lnk = '快捷方式'
    lnk_already_exist = '快捷方式已存在'


_lnk_files = 'lnk_files'
_shortcut = 'shortcut'
_auto_start = 'auto_start'
default_config = {
    _lnk_files: [],
    _shortcut: ["control", "q"],
    _auto_start: False
}
default_path = os.path.join(os.path.expanduser('~'), '.control-panel')
if not os.path.isdir(default_path):
    os.mkdir(default_path)
default_config_path = os.path.join(default_path, 'config.json')
default_log_path = os.path.join(default_path, 'log.log')


class Config(dict):
    def __init__(self, path=default_config_path):
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

    @property
    def shortcut(self):
        return self[_shortcut]

    @shortcut.setter
    def shortcut(self, value: list):
        self[_shortcut] = value

    @property
    def lnk_files(self) -> list:
        return self[_lnk_files]

    @property
    def auto_start(self) -> bool:
        return self[_auto_start]

    @auto_start.setter
    def auto_start(self, value: bool):
        if not isinstance(value, bool):
            value = False
        self[_auto_start] = value
