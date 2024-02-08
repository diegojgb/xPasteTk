import customtkinter
import darkdetect
import tkinter as tk
import pynput
import keyboard

# from Paster import Paster

from pynput.keyboard import Key, Listener


class HotkeyRecorder(tk.Entry):
    instances = []
    # Reference: (<background>, <border>, <highlight>, <font>)
    light = ('white', '#abadb3', '#7eb4ea', 'black')
    dark = ('#333', '#555', '#7eb4ea', 'white')

    def __init__(self, master, text='', width=15, *args, **kwargs) -> None:
        colors = self.get_colors(customtkinter.get_appearance_mode())
        self.text = tk.StringVar()
        self.set_text(text)
        self.keydown_id = None
        self.keyup_id = None

        super().__init__(master, borderwidth=0, width=width, justify='center', textvariable=self.text, state='readonly', foreground=colors[3],
                         readonlybackground=colors[0], highlightbackground=colors[1], highlightcolor=colors[2], highlightthickness=1, *args, **kwargs)
        HotkeyRecorder.instances.append(self)

        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)

        self.modifiers = {
            'ctrl': False,
            'shift': False,
            'alt': False,
            'win': False
        }
        self.key_map = {
            'Alt_L': 'alt',
            'Alt_R': 'alt',
            'Control_L': 'ctrl',
            'Control_R': 'ctrl',
            'Shift_L': 'shift',
            'Shift_R': 'shift',
            'Win_L': 'win',
            'Win_R': 'win'
        }
        self.current_key = ''

    # def keyup(self, e):
    #     if e.keysym in self.key_map:
    #         mod = self.key_map[e.keysym]
    #         self.modifiers[mod] = False
    #     keyboard.unblock_key('d')

    # def keydown(self, e):
    #     if e.keysym in self.key_map:
    #         mod = self.key_map[e.keysym]
    #         self.modifiers[mod] = True
    #     else:
    #         self.current_key = e.keysym
    #         self.set_text(self.get_current_hotkey())
    #     keyboard.block_key('d')

    # def get_current_hotkey(self):
    #     hotkey_str = '+'.join([mod for mod, bool in self.modifiers.items() if bool] + [self.current_key]).upper()
    #     return hotkey_str

    def focus_in(self, event):
        self.keydown_id = self.bind("<KeyPress>", self.keydown)
        self.keyup_id = self.bind("<KeyRelease>", self.keyup)

    def focus_out(self, event):
        self.unbind("<KeyPress>", self.keydown_id)
        self.unbind("<KeyRelease>", self.keyup_id)

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