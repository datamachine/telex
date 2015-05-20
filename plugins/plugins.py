import plugintypes
import json
import subprocess
import os
import uuid
import shutil
import re

from urllib.parse import urlparse

"""
Installable plugins are currently hardcoded here for early
development of the installation process. They will be centralized
online at a later date.

Plugin data will be downloaded in JSON format and inserted to a sqlite
database for local cache.
"""

PLUGINS_JSON="""
{
    "Whiskey": {
        "url": "https://github.com/xlopo/tg-pybot-whiskey",
        "description": "Pass the whiskey.",
        "version": "1.0"
    },
    "Example": {
        "url": "https://example.com",
        "description": "This is only an example.",
        "version": "0.1"
    }
}
"""

PLUGINS_REPOS_DIR="plugins.repos"
PLUGINS_TRASH_DIR="plugins.trash"
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
        "^!plugins? (install) (.*)$",
        "^!plugins? (uninstall) ([\w_.-]+)$",
        "^!plugins? (search) (.*)$",
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
        if not os.path.exists(PLUGINS_REPOS_DIR):
            os.makedirs(PLUGINS_REPOS_DIR)
        if PLUGINS_REPOS_DIR not in self.plugin_manager.getPluginLocator().plugins_places:
            self.plugin_manager.updatePluginPlaces([PLUGINS_REPOS_DIR])
            self.reload_plugins()

        self.plugins_repo = json.loads(PLUGINS_JSON)

    def run(self, msg, matches):
        if matches.group(0) == "!plugins":
            return self.list_plugins()

        command = matches.group(1)

        if command == "enable":
            return self.enable_plugin(matches)

        if command == "disable":
            return self.disable_plugin(matches)

        if command == "install":
            return self.install_plugin(matches)

        if command == "uninstall":
            return self.uninstall_plugin(matches)

        if command == "search":
            return self.search_plugins(matches.group(2))

        if command == "reload":
            return self.reload_plugins()

        

    def enable_plugin(self, matches):
        if self.plugin_manager.activatePluginByName(matches.group(2)):
            return "Enabled plugin: {}".format(matches.group(2))
        else:
            return "Error loading plugin: {}".format(matches.group(2))

    def disable_plugin(self, matches):
        if self.plugin_manager.deactivatePluginByName(matches.group(2)):
            return "Disabled plugin: {}".format(matches.group(2))
        else:
            return "Error disabling plugin: {}".format(matches.group(2))

    def __clone_repository(self, url):
            args = [GIT_BIN, "clone", url]
            p = subprocess.Popen(args, cwd=PLUGINS_REPOS_DIR)
            return p.wait()

    def install_plugin(self, matches):
        plugin = matches.group(2)
        urldata = urlparse(matches.group(2))

        url = None
        if urldata.scheme in [ "http", "https" ]:
            url = plugin
        elif plugin in self.plugins_repo.keys():
            url = self.plugins_repo[plugin]["url"]

        if not url:
            return "Invalid plugin or url: {}".format(plugin)

        if self.__clone_repository(url) != 0:
            return "Error installing plugin: {}".format(plugin)

        self.reload_plugins()

        return "Successfully installed plugin: {}".format(plugin)

    def uninstall_plugin(self, matches):
        plugin_name = matches.group(2)
        for plugin in self.plugin_manager.getAllPlugins():
            if plugin.name != plugin_name:
                continue

            plugin_dir = os.path.relpath(os.path.dirname(plugin.path))
            if not plugin_dir.startswith(PLUGINS_REPOS_DIR):
                return "Error uninstalling plugin: {}.\nCannot locate plugin directory.".format(plugin_name)

            while plugin_dir and os.path.dirname(plugin_dir) != PLUGINS_REPOS_DIR:
                plugin_dir = os.path.dirname(plugin_dir)

            if not plugin_dir:
                return "Error uninstalling plugin: {}.\nCannot locate plugin directory.".format(plugin_name)

            self.plugin_manager.deactivatePluginByName(plugin_name)

            old_base = os.path.basename(plugin_dir)
            new_base = "{}.{}".format(os.path.basename(plugin_dir), str(uuid.uuid4()))
            new_dir = os.path.join(PLUGINS_TRASH_DIR, new_base)
            shutil.move(plugin_dir, new_dir)

            return "Uninstalled plugin: {}".format(plugin_name)
        return "Unable to find plugin: {}".format(plugin_name)

    def search_plugins(self, query):
        prog = re.compile(query, flags=re.IGNORECASE)
        results = ""
        for plugin in self.plugins_repo:
            description = self.plugins_repo[plugin]["description"]
            if prog.search(plugin) or prog.search(description):
                results += "{} | {} | {}\n".format(plugin, self.plugins_repo[plugin]["version"], self.plugins_repo[plugin]["description"])
        return results

    def reload_plugins(self):
        self.plugin_manager.collectPlugins()
        return "Plugins reloaded"

    def list_plugins(self):
        text = ""
        for plugin in self.plugin_manager.getAllPlugins():
            text += "{0}: ({1})\n".format(plugin.name,
                                          "(Enabled)" if plugin.plugin_object.is_activated else "(Disabled)")

        return text
