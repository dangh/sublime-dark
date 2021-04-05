import sublime
import sublime_plugin


def get_color(mode):
    return sublime.ui_info()["system"]["style"] if mode == "system" else mode


def repaint(mode, settings):
    prefs = dict(dark=dict(), light=dict(), user=dict())
    changes = dict()
    if settings.get("dark_mode", "system") != mode:
        changes["dark_mode"] = mode
    color = get_color(mode)
    for key, value in settings.to_dict().items():
        for mode_ in ["dark", "light"]:
            suffix = ".{}".format(mode_)
            if key.endswith(suffix):
                user_key = key[0 : -len(suffix)]
                prefs[mode_][user_key] = value
                prefs["user"][user_key] = settings.get(user_key)
                break
    inverse_color = "dark" if color == "light" else "light"
    for key, value in prefs["user"].items():
        if key in prefs[color]:
            if prefs[color][key] != value:
                changes[key] = prefs[color][key]
        elif key in prefs[inverse_color]:
            if None != value:
                changes[key] = None
    if changes:
        settings.update(changes)
        sublime.save_settings("Preferences.sublime-settings")


class EventListener(sublime_plugin.EventListener):
    def on_activated_async(self, view):
        settings = sublime.load_settings("Preferences.sublime-settings")
        if settings.get("dark_mode", "system") == "system":
            repaint("system", settings)


class ToggleDarkModeCommand(sublime_plugin.ApplicationCommand):
    def run(self, mode):
        settings = sublime.load_settings("Preferences.sublime-settings")
        if settings.get("dark_mode", "system") != mode:
            repaint(mode, settings)
