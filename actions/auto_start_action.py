from PyQt5.Qt import *
from config import Config, FilesPath, StringsList
import winreg


class AutoStartAction(QAction):
    from main import MainWindow
    register_key = 'controlPanel'

    def __init__(self, parent: MainWindow, config: Config):
        super(AutoStartAction, self).__init__(parent=parent)
        self.config = config
        self.parent = parent

        self.triggered.connect(self.set_register)
        self.set_data()

    def set_data(self):
        if self.config.auto_start:
            self.setIcon(QIcon(FilesPath.image_auto_start_green))
            self.setText(StringsList.auto_start_close)
        else:
            self.setIcon(QIcon(FilesPath.image_auto_start_gray))
            self.setText(StringsList.auto_start_open)

    def set_register(self):
        self.config.auto_start = not self.config.auto_start
        self.set_data()

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
                             access=winreg.KEY_SET_VALUE)
        if self.config.auto_start:
            winreg.SetValueEx(key, self.register_key, 0, winreg.REG_SZ, self.parent.executable_path)
        else:
            try:
                winreg.DeleteValue(key, self.register_key)
            except FileNotFoundError:
                pass
        self.config.flush()
