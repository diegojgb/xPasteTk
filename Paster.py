import keyboard
import pyperclip


class Paster():
    def __init__(self, hotkey='CTRL+V') -> None:
        self._hotkey = hotkey
        self.is_listening = False

    def listen(self):
        keyboard.add_hotkey(self._hotkey, self.paste_from_clipboard, suppress=True)
        self.is_listening = True

    def stop_listening(self):
        keyboard.remove_hotkey(self._hotkey)
        self.is_listening = False

    def write(self, string):
        keyboard.write(string)

    def set_hotkey(self, new_hotkey):
        if new_hotkey != self._hotkey:
            if self.is_listening:
                self.stop_listening()
                self._hotkey = new_hotkey
                self.listen()
            else:
                self._hotkey = new_hotkey

    def get_hotkey(self):
        return self._hotkey

    def paste_from_clipboard(self):
        clipboard_content = pyperclip.paste()
        self.write(clipboard_content)