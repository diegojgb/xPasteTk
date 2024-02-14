import customtkinter
import keyboard
import tkinter as tk


class HotkeyRecorder(tk.Entry):
    instances = []
    colors = None

    def __init__(self, master, initial_state, command=lambda t: None, text='', width=15, *args, **kwargs) -> None:
        HotkeyRecorder.colors = HotkeyRecorder.get_colors(customtkinter.get_appearance_mode())
        colors = HotkeyRecorder.colors
        self.command = command
        self.mod_names = ['ctrl', 'shift', 'alt', 'cmd']
        self.text = tk.StringVar()
        self.set_hotkey(text)
        self.mods = []
        self.new_state = initial_state
        foreground = self.get_foreground(initial_state)
        highlightcolor = self.get_highlight_color(initial_state)

        super().__init__(master, borderwidth=0, width=width, justify='center', textvariable=self.text, state='disabled', disabledforeground=foreground,
                         disabledbackground=colors[0], highlightbackground=colors[1], highlightcolor=highlightcolor, highlightthickness=1, *args, **kwargs)
        HotkeyRecorder.instances.append(self)


    def set_state(self, state):
        if state != self.new_state:
            self.new_state = state
            self.set_state_colors()
            if state == 'normal':
                self.bind("<FocusIn>", self.start_recording)
                self.bind("<FocusOut>", self.stop_recording)
            else:
                self.unbind("<FocusIn>")
                self.unbind("<FocusOut>")

    def callback(self, e):
        if e.event_type == 'down':
            if e.name in self.mod_names:
                self.mods.append(e.name)
            else:
                self.set_hotkey(keyboard.get_hotkey_name(self.mods + [e.name]).upper())
        if e.event_type == 'up' and e.name in self.mod_names:
            self.mods.remove(e.name)

    def start_recording(self, event):
        keyboard.hook(self.callback, suppress=True)

    def stop_recording(self, event):
        keyboard.unhook(self.callback)
        self.command(self.get_hotkey())

    def get_foreground(self, state):
        return HotkeyRecorder.colors[3] if state == 'normal' else HotkeyRecorder.colors[4]

    def get_highlight_color(self, state):
        return HotkeyRecorder.colors[2] if state == 'normal' else HotkeyRecorder.colors[1]

    def set_state_colors(self):
        foreground = self.get_foreground(self.new_state)
        highlightcolor = self.get_highlight_color(self.new_state)
        self.configure(disabledforeground=foreground, highlightcolor=highlightcolor)

    def set_colors(self):
        colors = HotkeyRecorder.colors
        self.configure(disabledbackground=colors[0], highlightbackground=colors[1])
        self.set_state_colors()

    def set_hotkey(self, text):
        self.text.set(text)

    def get_hotkey(self):
        return self.text.get()

    @staticmethod
    def get_colors(mode):
        # Reference: (<background>, <border>, <highlight>, <enabled font>, <disabled font>)
        if mode == 'Light':
            return ('white', '#abadb3', '#7eb4ea', 'black', '#777')
        elif mode == 'Dark':
            return  ('#333', '#555', '#7eb4ea', 'white', '#AAA')

    @classmethod
    def set_color_for_all(cls, new_appearance_mode):
        cls.colors = cls.get_colors(new_appearance_mode)
        for instance in cls.instances:
            instance.set_colors()
