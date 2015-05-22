import plugintypes
import json
import subprocess
import uuid
import shutil
import re

import os
from os import path

import pip

from urllib.parse import urlparse

from tempfile import TemporaryFile

CENTRAL_REPO_URL="https://github.com/datamachine/telegram-pybot-plugin-repo"
CENTRAL_REPO_DIR="telegram-pybot-plugin-repo"

PLUGINS_REPOS_DIR="plugins.repos"
PLUGINS_TRASH_DIR="plugins.trash"

class PackageManagerPlugin(plugintypes.TelegramPlugin):
    """
    telegram-pybot's plugin package manager
    """
    patterns = [
        "^!pkg? (search) (.*)$",
        "^!pkg? (install) (.*)$",
        "^!pkg? (update)$",
        "^!pkg? (uninstall) ([\w_.-]+)$",
        "^!pkg? (installed)$",
    ]

    usage = [
        "!pkg search <query>: Search the repo for plugins",
        "!pkg update: Update the package repo cache",
        "!pkg upgrade: Update all plugins (not implemented)",
        "!pkg install <package name>: Install a package",
        "!pkg uninstall <package name>: Uninstall a package",
        "!pkg installed: List installed packages"
    ]

    @property
    def git_bin(self):
        if not self.has_option("git_bin"):
            self.write_option("git_bin", "/usr/bin/git")
        return self.read_option("git_bin")



    def __refresh_central_repo_object(self):
        try:
            with open(path.join(PLUGINS_REPOS_DIR, CENTRAL_REPO_DIR, "repo.json"), "r") as f:
                self.central_repo = json.load(f)
        except:
            print("Error opening repo.json")

    def activate_plugin(self):
        if not path.exists(PLUGINS_REPOS_DIR):
            os.makedirs(PLUGINS_REPOS_DIR)
        if PLUGINS_REPOS_DIR not in self.plugin_manager.getPluginLocator().plugins_places:
            self.plugin_manager.updatePluginPlaces([PLUGINS_REPOS_DIR])
            self.reload_plugins()
        else:
            self.__refresh_central_repo_object()

    def run(self, msg, matches):
        command = matches.group(1)
        if command == "install":
            return self.install_plugin(matches)

        if command == "uninstall":
            return self.uninstall_plugin(matches)

        if command == "search":
            return self.search_plugins(matches.group(2))

        if command == "update":
            return self.update_central_repo()

        if command == "installed":
            return self.get_installed()

    def __clone_repository(self, url):
            fp = TemporaryFile(mode="r")
            args = [self.git_bin, "clone", url]
            p = subprocess.Popen(args, cwd=PLUGINS_REPOS_DIR, stdout=fp, stderr=fp)
            code = p.wait()
            fp.seek(0)
            return (code, fp.read())

    def __get_repo_pkg_data(self, plugin_name):
        for pkg in self.central_repo["packages"]:
            if pkg["name"] == plugin_name:
                return pkg
        return None

    def __get_pkg_repo_path(self, pkg_name):
        for repo in os.listdir(PLUGINS_REPOS_DIR):
            repo_path = path.join(PLUGINS_REPOS_DIR, repo)
            repo_json_path = path.join(repo_path, "repository", "repo.json")
            try:
                with open(repo_json_path, 'r') as f:
                    repo_json = json.loads(f.read())
                    if repo_json["name"] == pkg_name:
                        print(repo_path)
                        return repo_path
                    continue
            except:
                continue 
        return None

    def __get_pkg_requirements_path(self, pkg_name):
        pkg_repo_path = self.__get_pkg_repo_path(pkg_name)
        if not pkg_repo_path:
            return None
        
        return path.join(pkg_repo_path, "repository", "requirements.txt")

    def install_plugin(self, matches):
        plugin = matches.group(2)
        urldata = urlparse(matches.group(2))

        url = None
        if urldata.scheme in [ "http", "https" ]:
            url = plugin
        else:
            pkg = self.__get_repo_pkg_data(plugin)
            if pkg:
                url = pkg["repo"]

        if not url:
            return "Invalid plugin or url: {}".format(plugin)

        code, msg = self.__clone_repository(url)
        if code != 0:
            return msg

        pkg_req_path = self.__get_pkg_requirements_path(plugin)
        print(pkg_req_path)
        if os.path.exists(pkg_req_path):
            pip.main(['install', '-r', pkg_req_path])

        self.reload_plugins()
 
        return "{}\nSuccessfully installed plugin: {}".format(msg, plugin)

    def uninstall_plugin(self, matches):
        plugin_name = matches.group(2)
        for plugin in self.plugin_manager.getAllPlugins():
            if plugin.name != plugin_name:
                continue

            plugin_dir = path.relpath(path.dirname(plugin.path))
            if not plugin_dir.startswith(PLUGINS_REPOS_DIR):
                return "Error uninstalling plugin: {}.\nCannot locate plugin directory.".format(plugin_name)

            while plugin_dir and path.dirname(plugin_dir) != PLUGINS_REPOS_DIR:
                plugin_dir = path.dirname(plugin_dir)

            if not plugin_dir:
                return "Error uninstalling plugin: {}.\nCannot locate plugin directory.".format(plugin_name)

            self.plugin_manager.deactivatePluginByName(plugin_name)

            old_base = path.basename(plugin_dir)
            new_base = "{}.{}".format(path.basename(plugin_dir), str(uuid.uuid4()))
            new_dir = path.join(PLUGINS_TRASH_DIR, new_base)
            shutil.move(plugin_dir, new_dir)

            return "Uninstalled plugin: {}".format(plugin_name)
        return "Unable to find plugin: {}".format(plugin_name)

    def search_plugins(self, query):
        prog = re.compile(query, flags=re.IGNORECASE)
        results = ""
        for pkg in self.central_repo["packages"]:
            if prog.search(pkg["name"]) or prog.search(pkg["description"]):
                results += "{} | {} | {}\n".format(pkg["name"], pkg["version"], pkg["description"])
        return results

    def update_central_repo(self):
        central_repo_path = path.join(PLUGINS_REPOS_DIR, CENTRAL_REPO_DIR)
        f = TemporaryFile()
        if not path.exists(central_repo_path):
            args = [self.git_bin, "clone", CENTRAL_REPO_URL]
            p = subprocess.Popen(args, cwd=PLUGINS_REPOS_DIR, stdout=f, stderr=f)
            p.wait()
        else:
            args = [self.git_bin, "reset", "--hard"]
            p = subprocess.Popen(args, cwd=central_repo_path, stdout=f, stderr=f)
            p.wait()
            args = [self.git_bin, "pull"]
            p = subprocess.Popen(args, cwd=central_repo_path, stdout=f, stderr=f)
            p.wait()
        self.__refresh_central_repo_object()
        f.seek(0)
        return f.read().decode('utf-8')

    def get_installed(self):
        pkgs = ""
        for f in os.listdir(PLUGINS_REPOS_DIR):
            pkgs += "{}\n".format(f)
        return pkgs
 
    def reload_plugins(self):
        self.plugin_manager.collectPlugins()
        return "Plugins reloaded"

    def list_plugins(self):
        return os.listdir(PLUGINS_REPOS_DIR)

