import multiprocessing
import customtkinter
import darkdetect
import tkinter as tk
import pynput
import keyboard

# from Paster import Paster

from pynput.keyboard import Key, Listener


def unwrapper(arg, **kwarg):
    return HotkeyRecorder.target_func(*arg, **kwarg)

class HotkeyRecorder(tk.Entry):
    instances = []
    # Reference: (<background>, <border>, <highlight>, <font>)
    light = ('white', '#abadb3', '#7eb4ea', 'black')
    dark = ('#333', '#555', '#7eb4ea', 'white')
    mod_names = ['ctrl', 'shift', 'alt', 'cmd']

    def __init__(self, master, text='', width=15, *args, **kwargs) -> None:
        colors = self.get_colors(customtkinter.get_appearance_mode())
        self.text = tk.StringVar()
        self.set_text(text)
        self.keydown_id = None
        self.keyup_id = None
        self.mods = []
        self.process = None

        super().__init__(master, borderwidth=0, width=width, justify='center', textvariable=self.text, state='readonly', foreground=colors[3],
                         readonlybackground=colors[0], highlightbackground=colors[1], highlightcolor=colors[2], highlightthickness=1, *args, **kwargs)
        HotkeyRecorder.instances.append(self)

        self.bind("<FocusIn>", self.start_recording)
        self.bind("<FocusOut>", self.stop_recording)


    def callback(self, e):
        if e.event_type == 'down':
            if e.name in HotkeyRecorder.mod_names:
                self.mods.append(e.name)
            else:
                self.set_text(keyboard.get_hotkey_name(self.mods + [e.name]).upper)
        if e.event_type == 'up' and e.name in HotkeyRecorder.mod_names:
            self.mods.remove(e.name)

    def target_func(self):
        keyboard.hook(self.callback, suppress=True)
        keyboard.wait('esc')

    def start_recording(self, event):
        self.process = multiprocessing.Process(target=unwrapper, args=zip([self]))
        self.process.start()

    def stop_recording(self, event):
        self.process.terminate()

    def set_text(self, text):
        self.text.set(text)

    def get_text(self):
        return self.text.get()

    def set_colors(self, colors):
        self.configure(background=colors[0], highlightbackground=colors[1], highlightcolor=colors[2], foreground=colors[3])

    @classmethod
    def get_colors(cls, mode):
        if mode == 'Light':
            return cls.light
        elif mode == 'Dark':
            return  cls.dark
        elif mode == 'System':
            return cls.dark if darkdetect.isDark() else cls.light

    @classmethod
    def set_color_for_all(cls, new_appearance_mode):
        colors = cls.get_colors(new_appearance_mode)
        for instance in cls.instances:
            instance.set_colors(colors)