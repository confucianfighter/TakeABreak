import json
import os


class SettingsManager:
    def __init__(self, file_path='settings.json'):
        self.file_path = file_path
        self.settings = self._load_settings()

    def _load_settings(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                json.dump({}, file)
            return {}
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def _save_settings(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.settings, file, indent=4)

    def get(self, key, default_value=None):
        return self.settings.get(key, default_value)

    def set(self, key, value):
        self.settings[key] = value
        self._save_settings()

settings = SettingsManager()