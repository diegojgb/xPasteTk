import os
import threading
import time
import tkinter as tk
import customtkinter
import darkdetect
from DoubleClickIcon import DoubleClickIcon
from Paster import Paster
from Settings import Settings
import colors
import pystray
import sys

from PIL import Image, ImageTk
from tkinter import ttk
from widgets.Checkbox import Checkbox
from widgets.CustomCombobox import CustomCombobox
from widgets.HotkeyRecorder import HotkeyRecorder
from widgets.LabelSeparator import LabelSeparator
from widgets.CustomLabelFrame import CustomLabelFrame
from widgets.TimeSpinbox import TimeSpinbox


DEFAULT_SETTINGS = {'start_minimized': 'False',
                    'one_click_open': 'False',
                    'hook_time': '00:00:00',
                    'hook_time_enabled': 'False',
                    'custom_hotkey_enabled': 'False',
                    'custom_hotkey': 'CTRL+V',
                    'listening': 'True'
                    }


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Initial configurations
        self.title("xPaste")
        self.geometry("700x375")
        self.resizable(False, False)
        self.style = ttk.Style()
        self.settings = Settings(DEFAULT_SETTINGS)
        self.paster = Paster(self.settings.get('custom_hotkey'))
        self.load_settings()

        def remove_focus(event):
            try:
                event.widget.focus_set()
            except:
                pass

        self.bind_all("<1>", remove_focus) # Widgets lose focus when clicked anywhere else.

        # TRAY ICON RELATED
        self.icon = DoubleClickIcon('xpaste_icon', 'xPaste', show=self.show_window, quit=self.quit_app, one_click=self.settings.get('one_click_open'),
                                    on_double_click=lambda: self.after(0, self.deiconify), image_path="assets/xpaste_logo.ico")
        self.icon_thread = threading.Thread(daemon=True, target=lambda: self.icon.run()).start()
        self.protocol('WM_DELETE_WINDOW', self.withdraw)

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        self.on_switch = customtkinter.CTkImage(Image.open(os.path.join(image_path, "on_switch.png")), size=(110, 45))
        self.off_switch = customtkinter.CTkImage(Image.open(os.path.join(image_path, "off_switch.png")), size=(110, 45))
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "xpaste_logo.png")), size=(54, 54))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(24, 24))
        self.settings_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "settings_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "settings_light.png")), size=(24, 24))
        self.about_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "about_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "about_light.png")), size=(24, 24))

        # NAVIGATION FRAME
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="", bg_color='#333',
                                                             image=self.on_switch if self.settings.get('listening') else self.off_switch)
        self.navigation_frame_label.bind("<Button-1>", self.switch_status)
        self.navigation_frame_label.grid(row=0, column=0, ipady=15, sticky='news')

        self.settings_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Settings",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.settings_image, anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=2, column=0, sticky="ew")

        self.about_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="About",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.about_image, anchor="w", command=self.about_button_event)
        self.about_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = CustomCombobox(self.navigation_frame, state="readonly",
                                                   values=["Light", "Dark", "System"],
                                                   command=self.change_appearance_mode_event)
        self.appearance_mode_menu.current(2)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")


        # SETTINGS FRAME
        # App settings
        self.settings_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.settings_frame.columnconfigure(1, weight=1)

        self.settings_label = customtkinter.CTkLabel(self.settings_frame, text="General settings",
                                                  font=customtkinter.CTkFont(size=20))

        self.settings_label.grid(row=0, column=0, padx=22, pady=(30, 0))
        self.app_settings_label = LabelSeparator(self.settings_frame, 'App settings').grid(row=1, column=0, columnspan=3, padx=(24, 33), pady=(15, 0), sticky="ews")

        self.checkbox1 = Checkbox(self.settings_frame, text='Start xPaste minimized to the system tray.',
                                  command=self.start_minimized_changed, initial_value=self.settings.get('start_minimized'))
        self.checkbox1.grid(row=2, column=0, columnspan=5, pady=(5, 0), padx=37, sticky='w')
        self.checkbox2 = Checkbox(self.settings_frame, text='Open from tray with a single click.', command=self.one_click_tray_changed,
                                  initial_value=self.settings.get('one_click_open'))
        self.checkbox2.grid(row=3, column=0, columnspan=5, pady=(1, 0), padx=37, sticky='w')

        # Clipboard hook settings
        self.app_settings_label = LabelSeparator(self.settings_frame, 'Clipboard hook settings').grid(row=4, column=0, columnspan=3, padx=(24, 33), pady=(15, 0), sticky="ews")

        self.time_frame = customtkinter.CTkFrame(self.settings_frame, fg_color='transparent')
        self.checkbox3 = Checkbox(self.time_frame, text='Automatically disable the hook after', command=self.time_checkbox_changed,
                                  initial_value=self.settings.get('hook_time_enabled'))
        self.checkbox3.grid(row=0, column=0)
        self.time_spinbox = TimeSpinbox(self.time_frame, command=self.time_spinbox_changed,
                                        initial_state='normal' if self.settings.get('hook_time_enabled') else 'disabled')
        self.time_spinbox.grid(row=0, column=1, padx=3)
        self.time_frame.grid(row=5, column=0, columnspan=5, pady=(5, 0), padx=37, sticky='w')

        self.hotkey_frame = customtkinter.CTkFrame(self.settings_frame, fg_color='transparent')
        self.checkbox4 = Checkbox(self.hotkey_frame, text='Setup a custom paste hotkey', command=self.hotkey_checkbox_changed,
                                  initial_value=self.settings.get('custom_hotkey_enabled'))
        self.checkbox4.grid(row=0, column=0)
        self.hotkey_recorder = HotkeyRecorder(self.hotkey_frame, text=self.paster.get_hotkey(), width=20, command=self.paster.set_hotkey,
                                              initial_state='normal' if self.settings.get('custom_hotkey_enabled') else 'disabled')
        self.hotkey_recorder.grid(row=0, column=1, padx=3, ipady=2.2)
        self.hotkey_frame.grid(row=6, column=0, columnspan=5, pady=(5, 0), padx=37, sticky='w')


        # ABOUT FRAME
        # Logo and App name
        self.about_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.about_frame.columnconfigure(2, weight=1)

        self.about_logo = customtkinter.CTkLabel(self.about_frame, text="", image=self.logo_image)
        self.app_name = customtkinter.CTkLabel(self.about_frame, text="xPaste",
                                                  font=customtkinter.CTkFont(size=20, weight="bold"))
        self.app_version = customtkinter.CTkLabel(self.about_frame, text="Version 2.0", anchor='nw',
                                                  font=customtkinter.CTkFont(size=14))

        self.about_logo.grid(row=0, column=0, padx=(24, 8), rowspan=2, pady=(30, 0))
        self.app_name.grid(row=0, column=1, pady=(31, 0), sticky="w")
        self.app_version.grid(row=1, column=1, pady=(1, 0), sticky='w')

        # Separator and author info
        self.author_separator = LabelSeparator(self.about_frame, 'Author info').grid(row=2, column=0, columnspan=3, padx=(25, 30), pady=(15, 0), sticky="ews")

        self.author_copyright = customtkinter.CTkLabel(self.about_frame, text="© 2024 - Obin XYZ", font=customtkinter.CTkFont(size=12), height=1)
        self.author_date = customtkinter.CTkLabel(self.about_frame, text="Release date: February 2024", font=customtkinter.CTkFont(size=12), height=1)
        self.author_copyright.grid(row=3, column=0, columnspan=3, padx=33, pady=(7, 0), sticky='w')
        self.author_date.grid(row=4, column=0, columnspan=3, sticky='w', pady=(2, 0), padx=45)


        # DEFAULT FRAME
        self.select_frame_by_name("settings")

        # Final configurations
        self.tk.call("source", "azure-ttk/azure.tcl")
        self.change_colors(customtkinter.get_appearance_mode())
        self.style.configure("TEntry", background="gray")


    def select_frame_by_name(self, name):
        # set button color for selected button
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")
        self.about_button.configure(fg_color=("gray75", "gray25") if name == "about" else "transparent")

        # show selected frame
        if name == "settings":
            self.settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.settings_frame.grid_forget()
        if name == "about":
            self.about_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.about_frame.grid_forget()

    def start_minimized_changed(self):
        self.settings.set('start_minimized', self.checkbox1.is_checked())

    def one_click_tray_changed(self):
        self.icon.set_one_click(self.checkbox2.is_checked())
        self.settings.set('one_click_open', self.checkbox2.is_checked())

    def time_checkbox_changed(self):
        self.settings.set('hook_time_enabled', self.checkbox3.is_checked())
        if self.checkbox3.is_checked():
            self.time_spinbox.set_state('normal')
        else:
            self.time_spinbox.set_state('disabled')

    def hotkey_checkbox_changed(self):
        self.settings.set('custom_hotkey_enabled', self.checkbox4.is_checked())
        if self.checkbox4.is_checked():
            self.hotkey_recorder.set_state('normal')
        else:
            self.hotkey_recorder.set_state('disabled')
            self.paster.set_hotkey('CTRL+V')

    def time_spinbox_changed(self):
        new_time = self.time_spinbox.get()
        self.settings.set('hook_time', new_time)

    def home_button_event(self):
        self.select_frame_by_name("home")

    def settings_button_event(self):
        self.select_frame_by_name("settings")

    def about_button_event(self):
        self.select_frame_by_name("about")

    def change_to_light(self):
        self.tk.call("set_theme", "light")

    def change_to_dark(self):
        self.tk.call("set_theme", "dark")

    def get_system_theme(self):
        return 'Dark' if darkdetect.isDark() else 'Light'

    def change_colors(self, new_appearance_mode):
        LabelSeparator.set_color_for_all(new_appearance_mode)
        HotkeyRecorder.set_color_for_all(new_appearance_mode)
        TimeSpinbox.set_color_for_all(new_appearance_mode)

        if new_appearance_mode == 'Light':
            self.change_to_light()
        elif new_appearance_mode == 'Dark':
            self.change_to_dark()

    def update_colors(self, mode):
        mode = mode if mode != 'System' else self.get_system_theme()

        if mode != customtkinter.get_appearance_mode():
            self.change_colors(mode)

    def change_appearance_mode_event(self, new_appearance_mode):
        self.update_colors(new_appearance_mode)
        customtkinter.set_appearance_mode(new_appearance_mode)

    def options_changed(self):
        pass

    def load_settings(self):
        if self.settings.get('listening'):
            self.paster.listen()
        if self.settings.get('start_minimized'):
            self.withdraw()

    def switch_status(self, e):
        if self.paster.is_listening:
            self.navigation_frame_label.configure(image=self.off_switch)
            self.paster.stop_listening()
            self.settings.set('listening', False)
        else:
            self.navigation_frame_label.configure(image=self.on_switch)
            self.paster.listen()
            self.settings.set('listening', True)

    def quit_app(self, icon):
        icon.stop()
        self.settings.save()
        self.quit()

    def show_window(self, icon):
        self.after(0, self.deiconify)


if __name__ == "__main__":
    app = App()
    app.iconbitmap("assets/xpaste_logo.ico")
    app.mainloop()