import tkinter as tk

from tkinter import ttk


class CustomCombobox(ttk.Combobox):
    def __init__(self, master, command=None, *arg, **kwarg):
        super().__init__(master, *arg, **kwarg)
        self.command = command
        self._strvar = tk.StringVar()
        self['textvariable'] = self._strvar
        self.bind("<<ComboboxSelected>>", self.on_value_selected)

    def on_value_selected(self, event):
        self.highlight_clear(event)
        self.command(self._strvar.get()) if self.command else None

    def highlight_clear(self, event):
        current = self._strvar.get()
        self.set("")
        self.set(current)