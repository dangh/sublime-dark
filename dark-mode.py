import sublime
import sublime_plugin
import re
import subprocess


def get_system_color():
    try:
        status = subprocess.check_output(
            "defaults read -g AppleInterfaceStyle".split()
        ).decode()
        return "dark" if re.search(r"dark", status, flags=re.I) else "light"
    except:
        return "light"


def get_color(mode):
    return get_system_color() if mode == "system" else mode


def repaint(color):
    settings = sublime.load_settings("Preferences.sublime-settings")
    prefs = dict(dark=dict(), light=dict(), user=dict())
    updated = False
    for key, value in settings.to_dict().items():
        for mode_ in ["dark", "light"]:
            suffix = ".{}".format(mode_)
            if key.endswith(suffix):
                user_key = key[0 : -len(suffix)]
                prefs[mode_][user_key] = value
                prefs["user"][user_key] = settings.get(user_key)
    inverse_mode = "dark" if color == "light" else "light"
    for key, value in prefs["user"].items():
        if key in prefs[color]:
            if prefs[color][key] != value:
                settings.set(key, prefs[color][key])
                updated = True
        elif key in prefs[inverse_mode]:
            settings.erase(key)
            updated = True
    if updated:
        sublime.save_settings("Preferences.sublime-settings")


class EventListener(sublime_plugin.EventListener):
    def on_activated_async(self, view):
        settings = sublime.load_settings("Preferences.sublime-settings")
        if settings.get("dark_mode", "system") == "system":
            repaint(get_system_color())


class ToggleDarkModeCommand(sublime_plugin.ApplicationCommand):
    def run(self, mode):
        settings = sublime.load_settings("Preferences.sublime-settings")
        if settings.get("dark_mode", "system") != mode:
            settings.set("dark_mode", mode)
            sublime.save_settings("Preferences.sublime-settings")
            repaint(get_color(mode))
