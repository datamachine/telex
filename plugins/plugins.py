import plugintypes
import json
import subprocess
import os



"""
Installable plugins are currently hardcoded here for early
development of the installation process. They will be centralized
online at a later date.

Plugin data will be downloaded in JSON format and inserted to a sqlite
database for local cache.
"""

PLUGIN_LINKS={ "Whiskey": "https://github.com/xlopo/tg-pybot-whiskey" }
REPO_DIR="plugins.repos"
GIT_BIN="/usr/bin/git"


class PluginsPlugin(plugintypes.TelegramPlugin):
    """
    Plugin to manage other plugins. Enable, disable or reload.
    """
    patterns = [
        "^!plugins$",
        "^!plugins? (enable) ([\w_.-]+)$",
        "^!plugins? (disable) ([\w_.-]+)$",
        "^!plugins? (install) ([\w_.-]+)$",
        # "^!plugins? (enable) ([\w_.-]+) (chat)",
        # "^!plugins? (disable) ([\w_.-]+) (chat)",
        "^!plugins? (reload)$"
    ]

    usage = [
        "!plugins: list all plugins.",
        "!plugins enable [plugin]: enable plugin.",
        "!plugins disable [plugin]: disable plugin.",
        # "!plugins disable [plugin] chat: disable plugin only this chat.",
        "!plugins reload: reloads all plugins."
    ]

    def activate_plugin(self):
        if not os.path.exists(REPO_DIR):
            os.makedirs(REPO_DIR)

    def run(self, msg, matches):
        if matches.group(0) == "!plugins":
            return self.list_plugins()

        if matches.group(1) == "enable":
            return self.enable_plugin(matches)

        if matches.group(1) == "disable":
            return self.disable_plugin(matches)

        if matches.group(1) == "install":
            return self.install_plugin(matches)

        if matches.group(1) == "reload":
            return self.reload_plugins()

    def enable_plugin(self, matches):
        if self.plugin_manager.activatePluginByName(matches.group(2)):
            return "Plugin {} enabled".format(matches.group(2))
        else:
            return "Error loading plugin {}".format(matches.group(2))

    def disable_plugin(self, matches):
        if self.plugin_manager.activatePluginByName(matches.group(2)):
            return "Plugin {} disabled".format(matches.group(2))
        else:
            return "Error disabling plugin {}".format(matches.group(2))

    def install_plugin(self, matches):
        plugin_name = matches.group(2)
        if plugin_name in PLUGIN_LINKS.keys():
            args = [GIT_BIN, "clone", PLUGIN_LINKS[plugin_name]]
            p = subprocess.Popen(args, cwd=REPO_DIR)
            repo_paths = os.listdir(REPO_DIR)
            plugin_paths = [os.path.join(REPO_DIR, repo) for repo in repo_paths]
            self.plugin_manager.getPluginLocator().updatePluginPlaces(plugin_paths)
        return ""

    def reload_plugins(self):
        self.plugin_manager.collectPlugins()
        return "Plugins reloaded"

    def list_plugins(self):
        text = ""
        for plugin in self.plugin_manager.getAllPlugins():
            text += "{0}: ({1})\n".format(plugin.name,
                                          "(Enabled)" if plugin.plugin_object.is_activated else "(Disabled)")

        return text
