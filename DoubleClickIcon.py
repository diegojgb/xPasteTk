import pystray

from PIL import Image


class DoubleClickIcon(pystray.Icon):
    WM_LBUTTONDBLCLK = 0x0203

    def __init__(self, name, title, show, quit, on_double_click, image_path, one_click=False, *args, **kwargs):
        self.one_click = one_click
        self.on_double_click = on_double_click

        self.new_menu = (
                pystray.MenuItem('Show', show, default=True, visible=False),
                pystray.MenuItem('Show', show),
                pystray.MenuItem('Exit', quit))
        icon = Image.open(image_path)

        super().__init__(name, icon, title, self.new_menu if one_click else self.new_menu[1:], *args, **kwargs)

    def _on_notify(self, wparam, lparam):
        super()._on_notify(wparam, lparam)
        if lparam == self.WM_LBUTTONDBLCLK and not self.one_click:
            self.on_double_click()

    def set_one_click(self, value):
        if self.one_click != value:
            if value:
                self.menu = pystray.Menu(lambda: self.new_menu)
            else:
                self.menu = pystray.Menu(lambda: self.new_menu[1:])
        self.one_click = value