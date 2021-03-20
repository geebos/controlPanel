from PyQt5.Qt import *
from extract_icon import get_icon_from_exe
from config import Config, FilesPath, StringsList
import actions
import system_hotkey
import win32com.client
import win32api
import sys
import subprocess
import traceback


class Item(QLabel):
    double_clicked = pyqtSignal()

    def __init__(self, parent, lnk_path):
        super(Item, self).__init__(parent=parent)
        self.lnk_path = lnk_path
        self.target = get_target_path(lnk_path)
        self.icon = get_icon_from_exe(self.target)
        self.setPixmap(QPixmap.fromImage(self.icon))
        self.setAlignment(Qt.AlignCenter)

        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setOffset(0, 0)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setBlurRadius(5)
        shadow_effect.setEnabled(False)
        self.setGraphicsEffect(shadow_effect)

        self.setStyleSheet('Item{background-color: white; border-radius: 4px;}')

    def mouseDoubleClickEvent(self, a0: QMouseEvent) -> None:
        subprocess.Popen(self.target)
        self.double_clicked.emit()

    def enterEvent(self, a0: QEvent) -> None:
        self.graphicsEffect().setEnabled(True)

    def leaveEvent(self, a0: QEvent) -> None:
        self.graphicsEffect().setEnabled(False)


class Container(QWidget):
    double_clicked = pyqtSignal()
    rows = 3
    cols = 6
    item_width = 42
    spacing = 20
    height = rows*item_width + (rows+1)*spacing
    width = cols*item_width + (cols+1)*spacing

    def __init__(self, parent=None):
        super(Container, self).__init__(parent=parent)

        self.items = []

        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setOffset(0, 0)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setBlurRadius(20)
        self.setGraphicsEffect(shadow_effect)

    def set_items(self, lnk_paths):
        self.items = []
        for lnk_path in lnk_paths:
            item = Item(self, lnk_path)
            item.setFixedSize(self.item_width, self.item_width)
            item.double_clicked.connect(self.double_clicked.emit)
            item.show()
            self.items.append(item)
        self.update_items()

    def add_item(self, lnk_path):
        item = Item(self, lnk_path)
        item.setFixedSize(self.item_width, self.item_width)
        item.double_clicked.connect(self.double_clicked.emit)
        item.show()
        self.items.append(item)
        self.update_items()

    def remove_item(self, item):
        item.deleteLater()
        self.items.remove(item)
        self.update_items()

    def update_items(self):
        row = 0
        col = 0
        for t in self.items:
            x = col * (self.spacing + self.item_width) + self.spacing
            y = row * (self.spacing + self.item_width) + self.spacing
            t.setGeometry(x, y, self.item_width, self.item_width)
            col += 1
            row += col // self.cols
            col %= self.cols
        self.repaint()


class MainWindow(QMainWindow):
    hot_key_emit = pyqtSignal()

    def __init__(self, executable_path):
        super(MainWindow, self).__init__()

        self.desktop = QApplication.desktop()
        self.config = Config()
        self.executable_path = executable_path

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setFocus()

        self.customContextMenuRequested.connect(self.show_context_menu)

        self.center_widget = Container(self)
        self.center_widget.double_clicked.connect(self.hide)
        self.center_widget.setObjectName('center_widget')
        self.center_widget.setAttribute(Qt.WA_StyledBackground, True)
        self.center_widget.setStyleSheet('QWidget#center_widget{background-color: rgba(255, 255, 255, 1); border-radius:8px}')
        self.center_widget.set_items(self.config.lnk_files)

        self.hot_key_manager = system_hotkey.SystemHotkey()
        self.hot_key_manager.register(self.config.shortcut, callback=lambda x: self.hot_key_emit.emit())
        self.hot_key_emit.connect(self.hot_key_emit_event)

        tray_icon = QSystemTrayIcon(parent=self)
        tray_icon.setIcon(QIcon(FilesPath.image_logo))
        tp_menu = QMenu()
        tp_menu.addAction(actions.AutoStartAction(self, self.config))
        tp_menu.addAction(actions.ExitAction(self, self.close))
        tray_icon.setContextMenu(tp_menu)
        tray_icon.show()
        self.tray_icon = tray_icon

    def hot_key_emit_event(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.hot_key_manager.unregister(self.config['shortcut'])
        self.tray_icon.setVisible(False)
        app.exit(0)

    def show(self) -> None:
        x, y = win32api.GetCursorPos()
        position = QPoint(x, y)
        screen_count = self.desktop.screenCount()
        screen_rect = None
        for i in range(screen_count):
            rect = self.desktop.screenGeometry(i)
            if position in rect:
                screen_rect = rect
                break
        self.setGeometry(screen_rect)
        self.center_widget.setGeometry(
            int((self.width()-self.center_widget.width)/2),
            int((self.height()-self.center_widget.height)/2),
            self.center_widget.width,
            self.center_widget.height
        )
        super(MainWindow, self).show()

    def add_lnk(self):
        filename, _ = QFileDialog.getOpenFileName(self, StringsList.select_lnk, '', '%s(*.lnk)' % StringsList.lnk)
        self.activateWindow()
        if filename == '':
            return

        if filename in self.config.lnk_files:
            QMessageBox.information(self, StringsList.hint, StringsList.lnk_already_exist)
            return
        self.config.lnk_files.append(filename)
        self.center_widget.add_item(filename)
        self.config.flush()

    def show_context_menu(self, point: QPoint):
        point = self.geometry().topLeft()+point
        menu = QMenu()
        menu.addAction(actions.AddLnkAction(self, self.add_lnk))

        item = QApplication.widgetAt(point)
        if type(item) is Item:
            menu.addAction(actions.DeleteLnkAction(self, lambda x: self.delete_item(item)))
        menu.exec_(point)

    def delete_item(self, item: Item):
        self.center_widget.remove_item(item)
        self.config.lnk_files.remove(item.lnk_path)
        self.config.flush()


def get_target_path(lnk_path):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(lnk_path)
    return shortcut.Targetpath


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        main = MainWindow(sys.argv[0])
        app.exec_()
    except:
        with open('log.log', 'a', encoding='utf-8') as f:
            f.write(traceback.format_exc()+'\n\n')
