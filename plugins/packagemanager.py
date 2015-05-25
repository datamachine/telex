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
CENTRAL_REPO_DIR="main"

PKG_BASE_DIR="pkgs"
PKG_REPO_DIR="pkgs/repos"
PKG_TRASH_DIR="pkgs/trash"
PKG_INSTALL_DIR="pkgs/installed"

class PackageManagerPlugin(plugintypes.TelegramPlugin):
    """
    telegram-pybot's plugin package manager
    """
    patterns = {
        "^!pkg? (search) (.*)$": "search",
        "^!pkg? (install) (.*)$": "install",
        "^!pkg? (update)$": "update",
        "^!pkg? (uninstall) ([\w_.-]+)$": "uninstall",
        "^!pkg? (list)$": "list_installed",
    }

    usage = [
        "!pkg search <query>: Search the repo for plugins",
        "!pkg update: Update the package repo cache",
        "!pkg upgrade: Update all plugins (not implemented)",
        "!pkg install <package name>: Install a package",
        "!pkg uninstall <package name>: Uninstall a package",
        "!pkg list: List installed packages"
    ]

    @property
    def git_bin(self):
        if not self.has_option("git_bin"):
            self.write_option("git_bin", "/usr/bin/git")
        return self.read_option("git_bin")



    def __refresh_central_repo_object(self):
        try:
            with open(path.join(PKG_REPO_DIR, CENTRAL_REPO_DIR, "repo.json"), "r") as f:
                self.central_repo = json.load(f)
        except:
            print("Error opening repo.json")

    def activate_plugin(self):
        if not path.exists(PKG_BASE_DIR):
            os.makedirs(PKG_BASE_DIR)
        if PKG_INSTALL_DIR not in self.plugin_manager.getPluginLocator().plugins_places:
            self.plugin_manager.updatePluginPlaces([PKG_INSTALL_DIR])
            self.reload_plugins()
        else:
            self.__refresh_central_repo_object()

    def __clone_repository(self, url, dst_dir):
            fp = TemporaryFile(mode="r")
            args = [self.git_bin, "clone", url, dst_dir]
            p = subprocess.Popen(args, cwd=PKG_INSTALL_DIR, stdout=fp, stderr=fp)
            code = p.wait()
            fp.seek(0)
            return (code, fp.read())

    def __get_repo_pkg_data(self, pkg_name):
        for pkg in self.central_repo["packages"]:
            if pkg["pkg_name"] == pkg_name:
                return pkg
        return None

    def __get_pkg_repo_path(self, pkg_name):
        for pkg in os.listdir(PKG_INSTALL_DIR):
            if pkg == pkg_name:
                return path.join(PKG_INSTALL_DIR, pkg)
        return None

    def __get_pkg_requirements_path(self, pkg_name):
        pkg_repo_path = self.__get_pkg_repo_path(pkg_name)
        if not pkg_repo_path:
            return None

        return path.join(pkg_repo_path, "repository", "requirements.txt")

    def __get_repo_json_from_repo_path(self, repo_path):
        repo_json_path = repo_json_path = path.join(repo_path, "repository", "repo.json")
        try:
            with open(repo_json_path, 'r') as f:
                return json.loads(f.read())
        except:
            pass
        return None
    
    def install(self, msg, matches):
        if not path.exists(PKG_INSTALL_DIR):
            os.makedirs(PKG_INSTALL_DIR)

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

        code, msg = self.__clone_repository(url, pkg["pkg_name"])
        if code != 0:
            return msg

        pkg_req_path = self.__get_pkg_requirements_path(plugin)
        if pkg_req_path and os.path.exists(pkg_req_path):
            pip.main(['install', '-r', pkg_req_path])

        self.reload_plugins()
 
        return "{}\nSuccessfully installed plugin: {}".format(msg, plugin)

    def uninstall(self, msg, matches):
        pkg_name = matches.group(2)
        for pkg in os.listdir(PKG_INSTALL_DIR):
            if pkg != pkg_name:
                continue

            pkg_path = path.join(PKG_INSTALL_DIR, pkg)

            trash_name = "{}.{}".format(path.basename(pkg_path), str(uuid.uuid4()))
            trash_path = path.join(PKG_TRASH_DIR, trash_name)
            shutil.move(pkg_path, trash_path)

            return "Uninstalled plugin: {}".format(pkg_name)
        return "Unable to find plugin: {}".format(pkg_name)

    def search(self, msg, matches):
        query = matches.group(2)
        prog = re.compile(query, flags=re.IGNORECASE)
        results = ""
        for pkg in self.central_repo["packages"]:
            if prog.search(pkg["name"]) or prog.search(pkg["description"]):
                results += "{} | {} | {}\n".format(pkg["pkg_name"], pkg["version"], pkg["description"])
        return results

    def update(self, msg, matches):
        if not path.exists(PKG_REPO_DIR):
            os.makedirs(PKG_REPO_DIR)

        central_repo_path = path.join(PKG_REPO_DIR, CENTRAL_REPO_DIR)
        f = TemporaryFile()
        if not path.exists(central_repo_path):
            args = [self.git_bin, "clone", CENTRAL_REPO_URL, CENTRAL_REPO_DIR]
            p = subprocess.Popen(args, cwd=PKG_REPO_DIR, stdout=f, stderr=f)
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

    def list_installed(self, msg, matches):
        pkgs = ""
        for f in os.listdir(PKG_INSTALL_DIR):
            repo_path = os.path.join(PKG_INSTALL_DIR, f)
            repo_json = self.__get_repo_json_from_repo_path(repo_path)
            if repo_json:
                pkgs += "{} | {} | {}\n".format(f, repo_json["version"], repo_json["description"])
        return pkgs
 
    def reload_plugins(self):
        self.plugin_manager.collectPlugins()
        return "Plugins reloaded"


