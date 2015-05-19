import plugintypes
import json
import subprocess
import os

from urllib.parse import urlparse

"""
Installable plugins are currently hardcoded here for early
development of the installation process. They will be centralized
online at a later date.

Plugin data will be downloaded in JSON format and inserted to a sqlite
database for local cache.
"""

PLUGIN_LINKS={ "Whiskey": "https://github.com/xlopo/tg-pybot-whiskey" }
PLUGIN_REPOS_DIR="plugins.repos"
PLUGINS_DIR="plugins"
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
        if not os.path.exists(PLUGIN_REPOS_DIR):
            os.makedirs(PLUGIN_REPOS_DIR)
        self.plugin_manager.updatePluginPlaces([PLUGIN_REPOS_DIR])

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

    def __clone_repository(self, url):
            args = [GIT_BIN, "clone", url]
            p = subprocess.Popen(args, cwd=PLUGIN_REPOS_DIR)
            return p.wait()

    def install_plugin(self, matches):
        plugin = matches.group(2)
        urldata = urlparse(matches.group(2))

        url = None
        if urldata.scheme in [ "http", "https" ]:
            url = plugin
        elif plugin in PLUGIN_LINKS.keys():
            url = PLUGIN_LINKS[plugin]

        if not url:
            return "Invalid plugin or url: {}".format(plugin)

        if not self.__clone_repository(url):
            return "Error installing plugin: {}".format(plugin)

        self.reload_plugins()

        return "Successfully installed plugin: {}".format(plugin)

    def reload_plugins(self):
        self.plugin_manager.collectPlugins()
        return "Plugins reloaded"

    def list_plugins(self):
        text = ""
        for plugin in self.plugin_manager.getAllPlugins():
            text += "{0}: ({1})\n".format(plugin.name,
                                          "(Enabled)" if plugin.plugin_object.is_activated else "(Disabled)")

        return text
