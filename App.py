import os
import threading
import customtkinter
import darkdetect
import keyboard
import winsdk.windows.ui.notifications as notifications
import winsdk.windows.data.xml.dom as dom
import sys

from DoubleClickIcon import DoubleClickIcon
from Paster import Paster
from Settings import Settings
from PIL import Image
from tkinter import ttk
from widgets.Countdown import Countdown
from widgets.Checkbox import Checkbox
from widgets.CustomCombobox import CustomCombobox
from widgets.HotkeyRecorder import HotkeyRecorder
from widgets.LabelSeparator import LabelSeparator
from widgets.TimeSpinbox import TimeSpinbox
from pyinstaller_utils import resource_path


DEFAULT_SETTINGS = {'start_minimized': 'False',
                    'one_click_open': 'False',
                    'hook_time': '00:00:00',
                    'hook_time_enabled': 'False',
                    'custom_hotkey_enabled': 'False',
                    'custom_hotkey': 'CTRL+D',
                    'listening': 'True',
                    'close_button_enabled': 'False',
                    'minimize_tray_enabled': 'False',
                    'toggle_hotkey_enabled': 'False',
                    'toggle_hotkey': '<not set>',
                    'disable_toast': 'False',
                    'disable_timer_toast': 'False',
                    'theme': 'System'
                    }
DEFAULT_HOTKEY = 'CTRL+V'
SWITCH_BG = {'Dark': '#333', 'Light': '#e4e4e4'}


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Initial configurations
        self.title("xPaste")
        self.geometry("700x475")
        self.resizable(False, False)
        self.prev_state = 'iconic'
        self.current_frame = None
        self.bind("<Unmap>", self.minimize_window_action)
        self.bind('<Map>', self.restore_window_action)
        self.settings = Settings(DEFAULT_SETTINGS)
        customtkinter.set_appearance_mode(self.settings.get('theme'))
        self.paster = Paster(self.settings.get('custom_hotkey') if self.settings.get('custom_hotkey_enabled') else DEFAULT_HOTKEY)
        self.countdown = Countdown(self, self.to_seconds(self.settings.get('hook_time')),
                                   title='xPaste - ', command=lambda: self.switch_status(countdown=True))

        def remove_focus(event):
            try:
                event.widget.focus_set()
            except:
                pass

        self.bind_all("<1>", remove_focus) # Widgets lose focus when clicked anywhere else.

        # TRAY ICON RELATED
        self.icon = DoubleClickIcon('xpaste_icon', 'xPaste', show=self.show_window, quit=self.quit_app, one_click=self.settings.get('one_click_open'),
                                    on_double_click=lambda: self.after(0, self.deiconify), image_path=resource_path("assets/xpaste_logo.ico"))
        self.icon_thread = threading.Thread(daemon=True, target=lambda: self.icon.run()).start()

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = resource_path("assets")
        self.on_switch = customtkinter.CTkImage(Image.open(os.path.join(image_path, "on_switch.png")), size=(110, 45))
        self.off_switch = customtkinter.CTkImage(Image.open(os.path.join(image_path, "off_switch.png")), size=(110, 45))
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "xpaste_logo.png")), size=(54, 54))
        self.settings_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "settings_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "settings_light.png")), size=(24, 24))
        self.about_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "about_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "about_light.png")), size=(24, 24))


        # NAVIGATION FRAME
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="", bg_color=SWITCH_BG[customtkinter.get_appearance_mode()],
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
        mapper = {'Light': 0, 'Dark': 1, 'System': 2}
        self.appearance_mode_menu.current(mapper[self.settings.get('theme')])
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
        self.checkbox5 = Checkbox(self.settings_frame, text='Close button exits the application.', command=self.close_button_changed,
                                  initial_value=self.settings.get('close_button_enabled'))
        self.checkbox5.grid(row=4, column=0, columnspan=5, pady=(1, 0), padx=37, sticky='w')
        self.checkbox6 = Checkbox(self.settings_frame, text='Minimize to the system tray.', command=self.minimize_tray_changed,
                                  initial_value=self.settings.get('minimize_tray_enabled'))
        self.checkbox6.grid(row=5, column=0, columnspan=5, pady=(1, 0), padx=37, sticky='w')

        # Clipboard hook settings
        self.app_settings_label = LabelSeparator(self.settings_frame, 'Clipboard hook settings').grid(row=6, column=0, columnspan=3, padx=(24, 33), pady=(15, 0), sticky="ews")

        self.hotkey_frame = customtkinter.CTkFrame(self.settings_frame, fg_color='transparent')
        self.checkbox4 = Checkbox(self.hotkey_frame, text='Setup a custom paste hotkey', command=self.custom_hotkey_checkbox_changed,
                                  initial_value=self.settings.get('custom_hotkey_enabled'))
        self.checkbox4.grid(row=0, column=0)
        self.custom_hotkey_recorder = HotkeyRecorder(self.hotkey_frame, text=self.paster.get_hotkey(), width=20, command=self.set_custom_hotkey,
                                              initial_state='normal' if self.settings.get('custom_hotkey_enabled') else 'disabled')
        self.custom_hotkey_recorder.grid(row=0, column=1, padx=3, ipady=2.2)
        self.hotkey_frame.grid(row=7, column=0, columnspan=5, pady=(5, 0), padx=37, sticky='w')

        self.toggle_hotkey_frame = customtkinter.CTkFrame(self.settings_frame, fg_color='transparent')
        self.toggle_hotkey_checkbox = Checkbox(self.toggle_hotkey_frame, text='Setup a hotkey for toggling the hook', command=self.toggle_hotkey_checkbox_changed,
                                  initial_value=self.settings.get('toggle_hotkey_enabled'))
        self.toggle_hotkey_checkbox.grid(row=0, column=0)
        self.toggle_hotkey_recorder = HotkeyRecorder(self.toggle_hotkey_frame, text=self.settings.get('toggle_hotkey'), width=20, command=self.update_toggle_hotkey,
                                              initial_state='normal' if self.settings.get('toggle_hotkey_enabled') else 'disabled')
        self.toggle_hotkey_recorder.grid(row=0, column=1, padx=3, ipady=2.2)
        self.toggle_hotkey_frame.grid(row=8, column=0, columnspan=5, pady=(6, 0), padx=37, sticky='w')

        self.toast_checkbox = Checkbox(self.settings_frame, text='Disable on/off notifications.', command=self.toast_checkbox_changed,
                                  initial_value=self.settings.get('disable_toast'),
                                  state='normal' if self.settings.get('toggle_hotkey_enabled') else 'disabled')
        self.toast_checkbox.grid(row=9, column=0, columnspan=5, pady=(3, 0), padx=64, sticky='w')

        self.time_frame = customtkinter.CTkFrame(self.settings_frame, fg_color='transparent')
        self.checkbox3 = Checkbox(self.time_frame, text='Automatically disable the hook after', command=self.time_checkbox_changed,
                                  initial_value=self.settings.get('hook_time_enabled'))
        self.checkbox3.grid(row=0, column=0)
        self.time_spinbox = TimeSpinbox(self.time_frame, command=self.time_spinbox_changed, initial_value=self.settings.get('hook_time'),
                                        initial_state='normal' if self.settings.get('hook_time_enabled') else 'disabled')
        self.time_spinbox.grid(row=0, column=1, padx=3)
        self.time_frame.grid(row=10, column=0, columnspan=5, pady=(6, 0), padx=37, sticky='w')

        self.timer_toast_checkbox = Checkbox(self.settings_frame, text="Disable \"Time's up\" notification.", command=self.timer_toast_checkbox_changed,
                                  initial_value=self.settings.get('disable_timer_toast'),
                                  state='normal' if self.settings.get('hook_time_enabled') else 'disabled')
        self.timer_toast_checkbox.grid(row=11, column=0, columnspan=5, pady=(3, 0), padx=64, sticky='w')


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


        # Final configurations
        self.select_frame_by_name("settings") # Default Frame
        self.tk.call("source", resource_path("azure-ttk/azure.tcl"))
        self.change_colors(customtkinter.get_appearance_mode())
        self.protocol("WM_DELETE_WINDOW", self.close_button_action)
        self.load_settings()

        def on_focus_out(event):
            if event.widget == self.time_spinbox:
                value = self.time_spinbox.get()
                if TimeSpinbox.is_valid(value):
                    new_value = self.time_spinbox.reformat()
                    if new_value != self.time_spinbox.focusin_value:
                        self.time_spinbox_changed()

        def on_focus_in(event):
            if event.widget == self.time_spinbox:
                self.time_spinbox.focusin_value = self.time_spinbox.get()

        self.bind("<FocusOut>", on_focus_out)
        self.bind("<FocusIn>", on_focus_in)

    def select_frame_by_name(self, name):
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")
        self.about_button.configure(fg_color=("gray75", "gray25") if name == "about" else "transparent")

        if name == "settings":
            self.settings_frame.grid(row=0, column=1, sticky="nsew")
            self.current_frame = self.settings_frame
        else:
            self.settings_frame.grid_forget()
        if name == "about":
            self.about_frame.grid(row=0, column=1, sticky="nsew")
            self.current_frame = self.about_frame
        else:
            self.about_frame.grid_forget()

    def start_minimized_changed(self):
        self.settings.set('start_minimized', self.checkbox1.is_checked())

    def one_click_tray_changed(self):
        self.icon.set_one_click(self.checkbox2.is_checked())
        self.settings.set('one_click_open', self.checkbox2.is_checked())

    def close_button_action(self):
        if self.checkbox5.is_checked():
            self.quit_app(self.icon)
        else:
            self.withdraw()
            self.current_frame.grid_forget()

    def close_button_changed(self):
        self.settings.set('close_button_enabled', self.checkbox5.is_checked())

    def restore_window_action(self, event):
        if self.prev_state in ('iconic', 'withdrawn'):
            self.current_frame.grid(row=0, column=1, sticky="nsew")
        self.prev_state = self.state()

    def minimize_window_action(self, event):
        if self.state() == 'iconic' and self.prev_state == 'normal':
            self.current_frame.grid_forget()
            if self.checkbox6.is_checked():
                self.withdraw()
        self.prev_state = self.state()

    def minimize_tray_changed(self):
        self.settings.set('minimize_tray_enabled', self.checkbox6.is_checked())

    def time_checkbox_changed(self):
        self.settings.set('hook_time_enabled', self.checkbox3.is_checked())
        if self.checkbox3.is_checked():
            self.time_spinbox.set_state('normal')
            self.timer_toast_checkbox.configure(state='normal')
            if self.paster.is_listening:
                self.countdown.start()
        else:
            self.time_spinbox.set_state('disabled')
            self.timer_toast_checkbox.configure(state='disabled')
            if self.paster.is_listening:
                self.countdown.stop()

    def custom_hotkey_checkbox_changed(self):
        self.settings.set('custom_hotkey_enabled', self.checkbox4.is_checked())
        if self.checkbox4.is_checked():
            self.custom_hotkey_recorder.set_state('normal')
            self.paster.set_hotkey(self.settings.get('custom_hotkey'))
        else:
            self.custom_hotkey_recorder.set_state('disabled')
            self.paster.set_hotkey(DEFAULT_HOTKEY)

    def set_custom_hotkey(self, new_hotkey):
        self.settings.set('custom_hotkey', new_hotkey)
        self.paster.set_hotkey(new_hotkey)

    def toggle_hotkey_checkbox_changed(self):
        self.settings.set('toggle_hotkey_enabled', self.toggle_hotkey_checkbox.is_checked())
        if self.toggle_hotkey_checkbox.is_checked():
            self.toast_checkbox.configure(state='normal')
            self.toggle_hotkey_recorder.set_state('normal')
            self.set_toggle_hotkey()
        else:
            self.toggle_hotkey_recorder.set_state('disabled')
            self.toast_checkbox.configure(state='disabled')
            self.unset_toggle_hotkey()

    def toast_checkbox_changed(self):
        self.settings.set('disable_toast', self.toast_checkbox.is_checked())

    def set_toggle_hotkey(self):
        hotkey = self.settings.get('toggle_hotkey')
        if hotkey != '<not set>':
            keyboard.add_hotkey(hotkey, lambda: self.switch_status(toast=True))

    def update_toggle_hotkey(self, new_hotkey):
        self.unset_toggle_hotkey()
        self.settings.set('toggle_hotkey', new_hotkey)
        self.set_toggle_hotkey()

    def unset_toggle_hotkey(self):
        hotkey = self.settings.get('toggle_hotkey')
        if hotkey != '<not set>':
            keyboard.remove_hotkey(hotkey)

    def time_spinbox_changed(self, *args):
        new_time = self.time_spinbox.get()
        self.settings.set('hook_time', new_time)
        self.time_spinbox.focusin_value = new_time
        self.countdown.duration = self.to_seconds(new_time)

        if self.paster.is_listening:
            if self.countdown.is_running():
                self.countdown.restart()
            else:
                self.countdown.start()

    def to_seconds(self, time_str):
        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            total_seconds = hours * 3600 + minutes * 60 + seconds
            return total_seconds
        except ValueError:
            print("Invalid time format. Please use HH:MM:SS.")

    def timer_toast_checkbox_changed(self):
        self.settings.set('disable_timer_toast', self.timer_toast_checkbox.is_checked())

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
        self.navigation_frame_label.configure(bg_color=SWITCH_BG[new_appearance_mode])

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
        self.settings.set('theme', new_appearance_mode)

    def load_settings(self):
        if self.settings.get('listening'):
            self.paster.listen()
            if self.settings.get('hook_time_enabled'):
                self.countdown.start()
        if self.settings.get('start_minimized'):
            self.withdraw()
        if self.settings.get('toggle_hotkey_enabled'):
            hotkey = self.settings.get('toggle_hotkey')
            if hotkey != '<not set>':
                keyboard.add_hotkey(hotkey, lambda: self.switch_status(toast=True))

    def switch_status(self, e=None, toast=False, countdown=False):
        disable_toast = self.settings.get('disable_toast')
        disable_timer_toast = self.settings.get('disable_timer_toast')

        if self.paster.is_listening:
            self.navigation_frame_label.configure(image=self.off_switch)
            self.paster.stop_listening()
            self.settings.set('listening', False)
            if not countdown and self.countdown.is_running():
                self.countdown.stop()
            if toast and not disable_toast:
                self.icon.notify('Hook OFF', 'Clipboard hook has been deactivated.')
            if countdown and not disable_timer_toast:
                self.icon.notify("Time's up!", 'Clipboard hook has been deactivated.')
        else:
            self.navigation_frame_label.configure(image=self.on_switch)
            self.paster.listen()
            self.settings.set('listening', True)
            if self.settings.get('hook_time_enabled'):
                self.countdown.start()
            if toast and not disable_toast:
                self.icon.notify('Hook ON', 'Clipboard hook has been activated.')

    def quit_app(self, icon):
        icon.stop()
        self.settings.save()
        self.quit()

    def show_window(self, icon):
        self.after(0, self.deiconify)

    def display_toast(self, title, content):
        nManager = notifications.ToastNotificationManager
        notifier = nManager.create_toast_notifier(sys.executable)

        logo_path = os.path.join(os.path.dirname(__file__), "assets/xpaste_logo.png")

        tString = f"""
        <toast>
            <visual>
                <binding template='ToastGeneric'>
                    <image placement="appLogoOverride" hint-crop="circle" src='{logo_path}'/>
                    <text>{title}</text>
                    <text>{content}</text>
                </binding>
            </visual>
        </toast>
        """

        xDoc = dom.XmlDocument()
        xDoc.load_xml(tString)
        notification = notifications.ToastNotification(xDoc)

        notifier.show(notification)
