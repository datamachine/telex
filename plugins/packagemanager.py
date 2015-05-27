import plugintypes
import json
import subprocess
import uuid
import shutil
import re
import sys

import os
from os import path

import pip

from urllib.parse import urlparse

from tempfile import TemporaryFile

from telegrambot import git

CENTRAL_REPO_URL="https://github.com/datamachine/telegram-pybot-plugin-repo"
CENTRAL_REPO_NAME="main"

PKG_BASE_DIR="pkgs"
PKG_REPO_DIR="pkgs/repos"
PKG_TRASH_DIR="pkgs/trash"
PKG_INSTALL_DIR="pkgs/installed"

class GitResponse:
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

class RepoObject:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def packages(self):
        return self.data["packages"]


class PackageManagerPlugin(plugintypes.TelegramPlugin):
    """
    telegram-pybot's plugin package manager
    """
    patterns = {
        "^!pkg? (search) (.*)$": "search",
        "^!pkg? (install) (.*)$": "install",
        "^!pkg? (update)$": "update",
        "^!pkg? upgrade$": "upgrade_all",
        "^!pkg? upgrade ([\w-]+)$": "upgrade_pkg",
        "^!pkg? (uninstall) (.*)$": "uninstall",
        "^!pkg? (list)$": "list_installed",
        "^!pkg? (list_all)$": "list_all",
    }

    usage = [
        "!pkg search <query>: Search the repo for plugins",
        "!pkg update: Update the package repo cache",
        "!pkg upgrade [pkg_name]: Update to latest version of all or specified pkg",
        "!pkg install <package name>: Install a package",
        "!pkg uninstall <package name>: Uninstall a package",
        "!pkg list: List installed packages"
        "!pkg list_all: List packages in the repo"
    ]

    def __repo_none_msg(self, repo_name):
        return "Repository \"{}\" not found. Try running \"!pkg update\"".format(repo_name)

    def __get_installed_repos(self):
        if path.exists(PKG_REPO_DIR):
            return os.listdir(PKG_REPO_DIR)
        return []

    def __get_repo_path(self, repo_name):
        if repo_name not in self.__get_installed_repos():
            return None
        return path.join(PKG_REPO_DIR, repo_name)

    def __load_repo_object(self, repo_name):
        repo_path = self.__get_repo_path(repo_name)
        if not repo_path:
            return None

        try:
            with open(path.join(repo_path, "repo.json"), "r") as f:
                data = json.load(f)
                return RepoObject(repo_name, data)
        except:
            print(sys.exc_info()[0])

        return None
        
    def __reload_central_repo_object(self, repo_name=CENTRAL_REPO_NAME):
        try:
            with open(path.join(PKG_REPO_DIR, CENTRAL_REPO_NAME, "repo.json"), "r") as f:
                self.central_repo = json.load(f)
                return True
        except:
            print(sys.exc_info()[0])
        return False

    def activate_plugin(self):
        self.central_repo = None
        self.repos = {}
        if not path.exists(PKG_BASE_DIR):
            os.makedirs(PKG_BASE_DIR)
        if PKG_INSTALL_DIR not in self.plugin_manager.getPluginLocator().plugins_places:
            self.plugin_manager.updatePluginPlaces([PKG_INSTALL_DIR])
            self.reload_plugins()
        else:
            self.__reload_central_repo_object()
            
    def __upgrade_pkg(self, pkg_name):
        args = [self.git_bin, "pull"]
        pkg_path = path.join(PKG_INSTALL_DIR, pkg_name)

        if not path.exists(pkg_path):
            return (None, "'{}' does not exist".format(pkg_path))

        fp = TemporaryFile(mode="r")
        p = subprocess.Popen(args, cwd=pkg_path, stdout=fp, stderr=fp)
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
        for plugin in matches.group(2).split():
            urldata = urlparse(matches.group(2))

            url = None
            if urldata.scheme in [ "http", "https" ]:
                url = plugin
            else:
                pkg = self.__get_repo_pkg_data(plugin)
                if pkg:
                    url = pkg["repo"]

            if not url:
                self.bot.get_peer_to_send(msg).send_msg("Invalid plugin or url: {}".format(plugin))

            code, status = self.__clone_repository(url, pkg["pkg_name"])
            if code != 0:
                self.bot.get_peer_to_send(msg).send_msg(status)

            pkg_req_path = self.__get_pkg_requirements_path(plugin)
            if pkg_req_path and os.path.exists(pkg_req_path):
                pip.main(['install', '-r', pkg_req_path])

            self.reload_plugins()
            if "default_enable" in pkg:
                for plugin_name in pkg["default_enable"]:
                    self.plugin_manager.activatePluginByName(plugin_name)

            self.bot.get_peer_to_send(msg).send_msg("{}\nSuccessfully installed plugin: {}".format(status, plugin))

    def upgrade_all(self, msg, matches):
        ret_msg = ""
        for pkg_name in os.listdir(PKG_INSTALL_DIR):
            ret_msg += "{}: {}\n".format(pkg_name, self.__upgrade_pkg(pkg_name)[1].strip())
        return ret_msg

    def upgrade_pkg(self, msg, matches):
        pkg_name = matches.group(1)
        return "{}: {}\n".format(pkg_name, self.__upgrade_pkg(pkg_name)[1])

    def uninstall(self, msg, matches):
        for pkg_name in matches.group(2).split():
            uninstalled = False
            for pkg in os.listdir(PKG_INSTALL_DIR):
                if pkg != pkg_name:
                    continue

                pkg_path = path.join(PKG_INSTALL_DIR, pkg)

                trash_name = "{}.{}".format(path.basename(pkg_path), str(uuid.uuid4()))
                trash_path = path.join(PKG_TRASH_DIR, trash_name)
                shutil.move(pkg_path, trash_path)

                self.bot.get_peer_to_send(msg).send_msg("Uninstalled plugin: {}".format(pkg_name))
                uninstalled = True
            if not uninstalled:
                self.bot.get_peer_to_send(msg).send_msg("Unable to find plugin: {}".format(pkg_name))

    def search(self, msg, matches):
        repo_name = CENTRAL_REPO_NAME
        if repo_name not in self.repos.keys():
            return "Repo not in cache. Try \"!pkg update {}\"".format(repo_name)

        repo = self.repos[repo_name]

        query = matches.group(2)
        prog = re.compile(query, flags=re.IGNORECASE)
        results = ""
        for pkg in repo.packages:
            if prog.search(pkg["name"]) or prog.search(pkg["description"]):
                results += "{} | {} | {}\n".format(pkg["pkg_name"], pkg["version"], pkg["description"])
        return results

    def update(self, msg, matches):
        repo_name = CENTRAL_REPO_NAME
        url = CENTRAL_REPO_URL

        if not path.exists(PKG_REPO_DIR):
            os.makedirs(PKG_REPO_DIR)

        gs = None
        if repo_name not in self.__get_installed_repos():
            gs = git.clone(url, directory=repo_name, cwd=PKG_REPO_DIR)
        else:
            repo_path = path.join(PKG_REPO_DIR, repo_name)
            git.reset(cwd=repo_path, hard=True)
            gs=git.pull(cwd=repo_path)

        if not gs:
            return "Error updating repo"

        if not gs.success():
            return "stdout:\n{}\nstderr:\n{}".format(gs.stdout, gs.stderr)

        repo_obj = self.__load_repo_object(repo_name)
        if not repo_obj:
            return "Error updating repo:\n{}".format(resp.msg)

        self.repos[repo_name] = repo_obj

        return "{}: {}{}".format(repo_name, gs.stdout, gs.stderr)

    def list_all(self, msg, matches):
        results = ""
        for pkg in self.central_repo["packages"]:
            results += "{} | {} | {}\n".format(pkg["pkg_name"], pkg["version"], pkg["description"])
        return results

    def list_installed(self, msg, matches):
        if not path.exists(PKG_INSTALL_DIR):
            return "There are no packages installed"

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


