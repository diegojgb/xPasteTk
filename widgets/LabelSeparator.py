import customtkinter
import tkinter as tk

class LabelSeparator(customtkinter.CTkFrame):
    instances = []

    def __init__(self, master, label, fontsize=14) -> None:
        customtkinter.CTkFrame.__init__(self, master, corner_radius=0, fg_color='transparent')
        LabelSeparator.instances.append(self)
        self.columnconfigure(2, weight=1)

        color = self.get_color(customtkinter.get_appearance_mode())
        self.separator = tk.Frame(self, bg=color, height=1, bd=0)
        self.separator.grid(row=0, column=1, columnspan=3, padx=(5, 0), pady=(4, 0), sticky="ew")

        self.label = self.app_version = customtkinter.CTkLabel(self, text=label, font=customtkinter.CTkFont(fontsize))
        self.label.grid(row=0, column=0)

    def set_color(self, color):
        self.separator.configure(bg=color)

    @staticmethod
    def get_color(mode):
        if mode == 'Light':
            return '#a0a0a0'
        elif mode == 'Dark':
            return '#777'

    @classmethod
    def set_color_for_all(cls, new_appearance_mode):
        color = cls.get_color(new_appearance_mode)
        for instance in cls.instances:
            instance.set_color(color)