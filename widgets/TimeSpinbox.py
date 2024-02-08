from tkinter import ttk
import tkinter as tk
import customtkinter


class TimeSpinbox(ttk.Spinbox):
    instances = []
    colors = None

    def __init__(self, master, initial_state, initial_value='00:00:00', *args, **kwargs):
        TimeSpinbox.instances.append(self)
        self.var = tk.StringVar()
        self.var.set(initial_value)
        TimeSpinbox.colors = TimeSpinbox.get_colors(customtkinter.get_appearance_mode())
        foreground_color = self.get_color(initial_state)
        self.state_value = initial_state

        super().__init__(master, width=15, values=self.time_values(), textvariable=self.var,
                         wrap=True, foreground=foreground_color, state=initial_state, *args, **kwargs)

    # Method created with ChatGPT
    def time_values(self):
        times = []
        for second in range(0, 86400):  # 86400 seconds in a day (24 hours * 60 minutes * 60 seconds)
            hour = second // 3600
            remaining_seconds = second - (hour * 3600)
            minutes = remaining_seconds // 60
            seconds = remaining_seconds - (minutes * 60)

            # Format each component to have leading zeros if less than 10
            hour_str = f'0{hour}' if hour < 10 else str(hour)
            minutes_str = f'0{minutes}' if minutes < 10 else str(minutes)
            seconds_str = f'0{seconds}' if seconds < 10 else str(seconds)

            times.append(f'{hour_str}:{minutes_str}:{seconds_str}')

        return times

    def set_state(self, state):
        if self.state_value != state:
            self.state_value = state
            self.configure(state=state)
            self.set_color()

    def set_color(self):
        self.configure(foreground=self.get_color(self.state_value))

    def get_color(self, state):
        return TimeSpinbox.colors[0] if state == 'normal' else TimeSpinbox.colors[1]

    @staticmethod
    # Reference: (<normal foreground>, <disabled foreground>)
    def get_colors(mode):
        if mode == 'Light':
            return ('black', '#777')
        elif mode == 'Dark':
            return ('white', '#AAA')

    @classmethod
    def set_color_for_all(cls, new_appearance_mode):
        cls.colors = cls.get_colors(new_appearance_mode)
        for instance in cls.instances:
            instance.set_color()