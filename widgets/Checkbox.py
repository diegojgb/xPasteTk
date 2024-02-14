import tkinter as tk

from tkinter import ttk


class Checkbox(ttk.Checkbutton):
    def __init__(self, master, initial_value=False, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.variable = tk.BooleanVar(self)
        self.variable.set(initial_value)
        self.config(variable=self.variable)

    def is_checked(self):
        return self.variable.get()

    def check(self):
        self.variable.set(True)

    def uncheck(self):
        self.variable.set(False)