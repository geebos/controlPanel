import win32ui
import win32gui
import win32con
import win32api
from PyQt5.Qt import QImage


def get_icon_from_exe(path):
    # refer: http://python.6.x6.nabble.com/Extract-icon-from-exe-files-td1948947.html
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)

    large, small = win32gui.ExtractIconEx(path, 0)
    win32gui.DestroyIcon(small[0])

    # creating a destination memory DC
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_x)
    hdc = hdc.CreateCompatibleDC()

    hdc.SelectObject(hbmp)

    # draw a icon in it
    hdc.FillSolidRect((0, 0, ico_x, ico_x), 0xffffff)
    hdc.DrawIcon((0, 0), large[0])
    win32gui.DestroyIcon(large[0])

    # convert picture
    hbmp.SaveBitmapFile(hdc, 'temp.bmp')
    return QImage('temp.bmp')
