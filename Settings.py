import os
from configparser import ConfigParser


class Settings():
    def __init__(self, settings, file='config.ini') -> None:
        self.config = ConfigParser()
        self.main_section = 'General'
        self.file = file

        if os.path.exists(file):
            self.config.read(file)
        else:
            self.config[self.main_section] = settings

    def set(self, setting, new_value):
        self.config.set(self.main_section, setting, str(new_value))

    def get(self, setting):
        value = self.config.get(self.main_section, setting)

        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        return value

    def save(self):
        with open(self.file, 'w') as configfile:
            self.config.write(configfile)
