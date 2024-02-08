import tkinter as tk
from tkinter import ttk

class CustomLabelFrame(ttk.LabelFrame):
    images = []

    def __init__(self, master, text, *arg, **kwarg) -> None:
        super().__init__(master, *arg, **kwarg)

        self.label = tk.Label(master, text=text, compound='center', borderwidth=0, highlightthickness=0, padx=0, pady=0)
        img_width = self.label.winfo_reqwidth()
        self.image = tk.PhotoImage(file='test.png', width=img_width).subsample(1, 3)
        CustomLabelFrame.images.append(self.image)
        self.label.config(image=self.image)
        self.config(labelwidget=self.label)