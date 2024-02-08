import pyperclip
import keyboard
import pynput
import time

from pynput.keyboard import Key


class Paster():
    def __init__(self) -> None:
        self._ctrl_pressed = False
        self._alt_pressed = False
        self.listener = self._keyboard_listener()

    def listen(self):
        with self.listener as listener:
            print('Listening to key presses...')
            listener.join()

    def write(self, string):
        keyboard.write(string)

    def paste_from_clipboard(self):
        clipboard_content = pyperclip.paste()
        self.write(clipboard_content)

    def _on_press(self, key):
        if (key == Key.ctrl_l) | (key == Key.ctrl_r):
            self._ctrl_pressed = True
        if (key == Key.alt_l) | (key == Key.alt_r):
            self._alt_pressed = True

    def _on_release(self, key):
        if (key == Key.ctrl_l) | (key == Key.ctrl_r):
            self._ctrl_pressed = False
        if (key == Key.alt_l) | (key == Key.alt_r):
            self._alt_pressed = False

    def _win32_event_filter(self, msg, data):
        if (msg == 257 or msg == 256) and self._ctrl_pressed and data.vkCode == 86:  # Key Down/Up & Ctrl+V
            self.listener._suppress = True
            self.paste_from_clipboard()
        else:
            self.listener._suppress = False
        return True

    def _keyboard_listener(self):
        return pynput.keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            win32_event_filter=self._win32_event_filter
        )