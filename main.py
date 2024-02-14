from App import App
from pyinstaller_utils import resource_path


if __name__ == "__main__":
    app = App()
    app.iconbitmap(resource_path("assets/xpaste_logo.ico"))
    app.mainloop()