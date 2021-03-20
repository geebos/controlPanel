from .auto_start_action import AutoStartAction
from .simple_action import SimpleAction
from config import StringsList, FilesPath


__all__ = ['AutoStartAction', 'ExitAction', 'AddLnkAction', 'DeleteLnkAction']


class ExitAction(SimpleAction):
    def __init__(self, parent, callback):
        super(ExitAction, self).__init__(parent, FilesPath.image_exit, StringsList.exit, callback)


class AddLnkAction(SimpleAction):
    def __init__(self, parent, callback):
        super(AddLnkAction, self).__init__(parent, FilesPath.image_add_lnk, StringsList.add_lnk, callback)


class DeleteLnkAction(SimpleAction):
    def __init__(self, parent, callback):
        super(DeleteLnkAction, self).__init__(parent, FilesPath.image_delete_lnk, StringsList.delete_lnk, callback)
