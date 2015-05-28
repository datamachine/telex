import plugintypes
import json
import subprocess
import uuid
import shutil
import re
import sys

from pathlib import Path

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
        "^!pkg? (list all)$": "list_all",
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

    def _installed_repos(self):
        if path.exists(PKG_REPO_DIR):
            return os.listdir(PKG_REPO_DIR)
        return []

    def _repo_path(self, repo_name):
        return path.join(PKG_REPO_DIR, repo_name)

    def _load_repo_object(self, repo_name):
        repo_file = Path(PKG_REPO_DIR) / repo_name / "repo.json"
        try:
            with repo_file.open('r') as f:
                return json.load(f)
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

    def _reload_repos(self, msg=None):
        self.repos = {}
        for repo_name in os.listdir(PKG_REPO_DIR):
            repo_json = self._load_repo_object(repo_name)
            if repo_json:
                self.repos[repo_name] = repo_json               
            elif msg:
                self.respond_to_msg(msg, "Error reloading repo: {}".format(repo_name))
            

    def activate_plugin(self):
        self.central_repo = None
        self.repos = {}
        if not path.exists(PKG_BASE_DIR):
            os.makedirs(PKG_BASE_DIR)
        if PKG_INSTALL_DIR not in self.plugin_manager.getPluginLocator().plugins_places:
            self.plugin_manager.updatePluginPlaces([PKG_INSTALL_DIR])
            self.reload_plugins()

        self._reload_repos()
            
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

    def _get_repo(self, repo_name):
        return self.repos.get(repo_name, None)

    def _pkg_data_from_repo(self, pkg_name, repo_name):
        repo = self._get_repo(repo_name)
        for pkg in repo.get("packages",[]):
            if pkg["pkg_name"] == pkg_name:
                return pkg
        return None

    def _pkg_repo_path(self, pkg_name):
        return path.join(PKG_INSTALL_DIR, pkg_name)

    def _pkg_requirements_path(self, pkg_name):
        return path.join(self._pkg_repo_path(pkg_name), "repository", "requirements.txt")

    def __get_repo_json_from_repo_path(self, repo_path):
        repo_json_path = repo_json_path = path.join(repo_path, "repository", "repo.json")
        try:
            with open(repo_json_path, 'r') as f:
                return json.loads(f.read())
        except:
            pass
        return None

    def install(self, msg, matches):
        repo_name = CENTRAL_REPO_NAME

        if not path.exists(PKG_INSTALL_DIR):
            os.makedirs(PKG_INSTALL_DIR)

        for pkg_name in matches.group(2).split():
            url = None
            pkg_data = None

            if urlparse(matches.group(2)).scheme in ["http", "https"]:
                url = pkg_name
            else:
                pkg_data = self._pkg_data_from_repo(pkg_name, repo_name)
                if pkg_data:
                    url = pkg_data["repo"]

            if not url:
                self.respond_to_msg(msg, "Invalid plugin or url: {}".format(pkg_name))

            gs = git.clone(url, pkg_data["pkg_name"], cwd=PKG_INSTALL_DIR)
            if gs.has_error():
                self.respond_to_msg(msg, "{}{}".format(gs.stdout, gs.stderr))

            pkg_req_path = self._pkg_requirements_path(pkg_name)
            if os.path.exists(pkg_req_path):
                pip.main(['install', '-r', pkg_req_path])

            self.reload_plugins()
            for plugin_name in pkg_data.get("default_enable", []):
                self.plugin_manager.activatePluginByName(plugin_name)

            self.respond_to_msg(msg, "{}{}\nSuccessfully installed package: {}".format(gs.stdout, gs.stderr, pkg_name))

    def upgrade_all(self, msg, matches):
        ret_msg = ""
        for pkg_name in os.listdir(PKG_INSTALL_DIR):
            ret_msg += "{}: {}\n".format(pkg_name, self.__upgrade_pkg(pkg_name)[1].strip())
        return ret_msg

    def upgrade_pkg(self, msg, matches):
        pkg_name = matches.group(1)
        return "{}: {}\n".format(pkg_name, self.__upgrade_pkg(pkg_name)[1])

    def uninstall(self, msg, matches):
        install_dir = Path(PKG_INSTALL_DIR)
        trash_dir = Path(PKG_TRASH_DIR)

        if not trash_dir.exists():
            trash_dir.mkdir(parents=True)
        
        for pkg_name in matches.group(2).split():
            pkg_path = install_dir / pkg_name

            if not pkg_path.exists():
                continue

            trash_path = trash_dir / "{}.{}".format(pkg_name, str(uuid.uuid4()))
            pkg_path.rename(trash_path)
            self.respond_to_msg(msg, "Uninstalled plugin: {}".format(pkg_name))
            return

        self.respond_to_msg(msg, "Unable to find plugin: {}".format(pkg_name))

    def search(self, msg, matches):
        repo_name = CENTRAL_REPO_NAME
        if repo_name not in self.repos.keys():
            return "Repo not in cache. Try \"!pkg update {}\"".format(repo_name)

        repo = self._get_repo(repo_name)
        if not repo:
            self.respond_to_msg(msg, "Cannot locate repo \"{}\"\nTry running !pkg update".format(repo_name))
            return

        query = matches.group(2)
        prog = re.compile(query, flags=re.IGNORECASE)
        results = ""
        for pkg in repo.get("packages", []):
            if prog.search(pkg["name"]) or prog.search(pkg["description"]):
                results += "{} | {} | {}\n".format(pkg["pkg_name"], pkg["version"], pkg["description"])
        return results

    def update(self, msg, matches):
        repo_name = CENTRAL_REPO_NAME
        url = CENTRAL_REPO_URL
        pkg_repo_dir = Path(PKG_REPO_DIR)

        if not pkg_repo_dir.exists():
            pkg_repo_dir.mkdir(parents=True)

        gs = None
        if repo_name not in self._installed_repos():
            gs = git.clone(url, directory=repo_name, cwd=PKG_REPO_DIR)
        else:
            repo_path = self._repo_path(repo_name)
            git.reset(cwd=repo_path, hard=True)
            gs = git.pull(cwd=repo_path)

        if not gs:
            self.respond_to_msg(msg, "Unkown error updating repo: {}".format(repo_name))
            return

        if not gs.has_error():
            self._reload_repos(msg)

        self.respond_to_msg(msg, "{}: {}{}".format(repo_name, gs.stdout, gs.stderr))

    def list_all(self, msg, matches):
        repo_name = CENTRAL_REPO_NAME
        results = ""
        for pkg in self.repos.get(repo_name, {}).get("packages", []):
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


