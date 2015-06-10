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

from telex import git, auth, plugin, packagerepo


CENTRAL_REPO_NAME="main"

PKG_BASE_DIR="pkgs"
PKG_REPO_DIR="pkgs/repos"
PKG_TRASH_DIR="pkgs/trash"
PKG_INSTALL_DIR="pkgs/installed"

class PackageManagerPlugin(plugin.TelexPlugin):
    """
    telegram-pybot's package manager
    """
    patterns = {
        "^{prefix}pkg? (search) (.*)$": "search",
        "^{prefix}pkg? install ((?P<repo_name>\S*)/){0,1}(?P<pkg_name>\S*)": "install",
        "^{prefix}pkg? (update)$": "update",
        "^{prefix}pkg? upgrade$": "upgrade_all",
        "^{prefix}pkg? upgrade ([\w-]+)$": "upgrade_pkg",
        "^{prefix}pkg? (uninstall) (.*)$": "uninstall",
        "^{prefix}pkg? (list)$": "list_installed",
        "^{prefix}pkg? (list[\s_]all)$": "list_all",
        "^{prefix}pkg list[\s_]repos$": "list_repos",
        #"^{prefix}pkg? add[\s_]repo (?P<repo_name>[\w\-]+) (?P<repo_url>[\S]+)$": "add_repo",
    }

    usage = [
        "Package Command:",
        "{prefix}pkg search <query>: Search the repo for packages",
        "{prefix}pkg update: Update the package repo cache",
        "{prefix}pkg upgrade [pkg_name]: Update to latest version of all or specified pkg",
        "{prefix}pkg install <package name>: Install a package",
        "{prefix}pkg uninstall <package name>: Uninstall a package",
        "{prefix}pkg list: List installed packages",
        "{prefix}pkg list all: List packages in the repo",
        "Repository Commands:",
        "{prefix}pkg list repos",
        #"{prefix}pkg add repo <repo_name>",
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
        
    def _reload_repos(self, msg=None):
        pkg_repo_dir = Path(PKG_REPO_DIR)
        if not pkg_repo_dir.exists():
            pkg_repo_dir.mkdir(parents=True)

        repos = self._get_repos_from_config()
        self.repos = {}
        for repo in pkg_repo_dir.iterdir():
            if repo.name not in repos:
                continue 
            repo_json = self._load_repo_object(repo.name)
            if repo_json:
                self.repos[repo.name] = repo_json               
            elif msg:
                self.respond_to_msg(msg, "Error reloading repo: {}".format(repo.name))
            

    def activate_plugin(self):
        if not self._get_repos_from_config():
            self.write_option('repo.main', 'https://github.com/datamachine/telex-plugin-repo.git')

        self.repos = {}
        if not path.exists(PKG_BASE_DIR):
            os.makedirs(PKG_BASE_DIR)
        if PKG_INSTALL_DIR not in self.plugin_manager.getPluginLocator().plugins_places:
            self.plugin_manager.updatePluginPlaces([PKG_INSTALL_DIR])
            self.reload_plugins()

        self._reload_repos()
            
    def _get_repo(self, repo_name):
        return self.repos.get(repo_name, None)

    def _pkg_data_from_repo(self, pkg_name, repo_name):
        for pkg in self.repos.get(repo_name, {}).get("packages",[]):
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

    @auth.authorize(groups=["admins"])
    def install(self, msg, matches):
        if not self.repos:
            self.respond_to_msg(msg, "Cannot locate repo. Try running \"{prefix}pkg update\"")
            return

        repo_name = matches.groupdict()['repo_name']
        pkg_name = matches.groupdict()['pkg_name']

        if not repo_name:
            repos_with_pkg = []
            for r in self.repos:
                for pkg in self.repos[r]['packages']:
                    if pkg['pkg_name'] == pkg_name:
                        repos_with_pkg.append(r)

            if not repos_with_pkg:
                self.respond_to_msg(msg, 'Cannot find pkg "{}" in any repos.\nTry running "{prefix}pkg update"'.format(pkg_name))
                return

            if len(repos_with_pkg) > 1:
                self.respond_to_msg(msg, 'Package "{}" found in multiple repos. Please specify repo using:\n <repo_name>/<pkg_name>\nRepos with package: {}'.format(pkg_name, ', '.join(repos_with_pkg)))
                return

            repo_name = repos_with_pkg[0]

        pkg_data = self._pkg_data_from_repo(pkg_name, repo_name)
        if not pkg_data:
            self.respond_to_msg(msg, 'Package "{}" not found in repository "{}"'.format(pkg_name, repo_name))
            return
    
        url = pkg_data["repo"]
        if not url:
            self.respond_to_msg(msg, 'Error: unable to retrieve url for package "{}"'.format(pkg_name))
            return

        pkg_inst_path = Path(PKG_INSTALL_DIR)
        if not pkg_inst_path.exists():
            pkg_inst_path.mkdir(parents=True)

        gs = git.clone(url, pkg_data["pkg_name"], cwd=str(pkg_inst_path))
        if gs.has_error():
            self.respond_to_msg(msg, "Error installing package \"{}\"\n{}{}".format(pkg_name, gs.stdout, gs.stderr))
            return

        pkg_req_path = pkg_inst_path / pkg_name / "repository" / "requirements.txt"
        print('\n\n{}\n\n'.format(pkg_req_path))
        if pkg_req_path.exists():
            pip.main(['install', '--upgrade', '-r', str(pkg_req_path)])

        self.reload_plugins()
        for plugin_name in pkg_data.get("default_enable", []):
            self.plugin_manager.activatePluginByName(plugin_name)

        self.plugin_manager.collectPlugins()
        self.respond_to_msg(msg, "{}{}\nSuccessfully installed package: {}".format(gs.stdout, gs.stderr, pkg_name))

    def _upgrade_pkg(self, msg, pkg_name):
        pkg_path = Path(PKG_INSTALL_DIR) / pkg_name
        if not pkg_path.exists():
            self.respond_to_msg(msg, "Cannot upgrade \"{}\". Package does not appear to be installed.".format(pkg_name))

        gs = git.pull(str(pkg_path))

        pkg_req_path = Path(PKG_INSTALL_DIR) / pkg_name / "repository" / "requirements.txt"
        print('\n\n{}\n\n'.format(pkg_req_path))
        if pkg_req_path.exists():
            pip.main(['install', '--upgrade', '-r', str(pkg_req_path)])

        self.respond_to_msg(msg, "{} {}: {}{}".format(gs.exit_status, pkg_name, gs.stdout, gs.stderr))
        

    @auth.authorize(groups=["admins"])
    def upgrade_all(self, msg, matches):
        if not path.exists(PKG_INSTALL_DIR):
            self.respond_to_msg(msg, "Nothing to update. It appears that there are no packages installed.")
            return

        for pkg_name in os.listdir(PKG_INSTALL_DIR):
            self._upgrade_pkg(msg, pkg_name)

    @auth.authorize(groups=["admins"])
    def upgrade_pkg(self, msg, matches):
        pkg_name = matches.group(1)
        self._upgrade_pkg(msg, pkg_name)

    @auth.authorize(groups=["admins"])
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
            self.respond_to_msg(msg, "Uninstalled package: {}".format(pkg_name))
            return

        self.respond_to_msg(msg, "Unable to find package: {}".format(pkg_name))

    def search(self, msg, matches):
        if not self.repos:
            self.respond_to_msg(msg, "Cannot locate repo. Try running \"{prefix}pkg update\"")
            return

        for repo_name in self.repos:
            repo = self._get_repo(repo_name)

            query = matches.group(2)
            prog = re.compile(query, flags=re.IGNORECASE)
            results = "{}:\n".format(repo_name)
            for pkg in repo.get("packages", []):
                if prog.search(pkg["name"]) or prog.search(pkg["description"]):
                    results += "{} | {} | {}\n".format(pkg["pkg_name"], pkg["version"], pkg["description"])
            self.respond_to_msg(msg, results)

    def _get_repos_from_config(self):
        return { name[5:]: self.read_option(name) for name in self.all_options() if name.startswith('repo.') }

    @auth.authorize(groups=["admins"])
    def update(self, msg, matches):
        repos = self._get_repos_from_config()

        if not repos:
            self.respond_to_msg(msg, "Warning: there are no repos in the configuration")
            return

        pkg_repo_dir = Path(PKG_REPO_DIR)
        if not pkg_repo_dir.exists():
            pkg_repo_dir.mkdir(parents=True)

        for repo_name, url in repos.items():
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
        if not self.repos: 
            self.respond_to_msg(msg, "Cannot locate repo. Try running \"{prefix}pkg update\".")
            return

        for repo_name in self.repos:
            results = "{}:\n".format(repo_name)
            for pkg in self.repos.get(repo_name, {}).get("packages", []):
                results += "{} | {} | {}\n".format(pkg["pkg_name"], pkg["version"], pkg["description"])
            self.respond_to_msg(msg, results)

    def list_installed(self, msg, matches):
        pkg_install_dir = Path(PKG_INSTALL_DIR)
        if not pkg_install_dir.exists():
            return "There are no packages installed"

        pkgs = ''
        for pkg_name in os.listdir(PKG_INSTALL_DIR):
            repo_path = os.path.join(PKG_INSTALL_DIR, pkg_name)
            repo_json = self.__get_repo_json_from_repo_path(repo_path)
            if repo_json:
                pkgs += "{} | {} | {}\n".format(pkg_name, repo_json["version"], repo_json["description"])
        self.respond_to_msg(msg, pkgs)

    @auth.authorize(groups=["admins"])
    def add_repo(self, msg, matches):
        repo_name = matches.groupdict()["repo_name"]
        repo_url = matches.groupdict()["repo_url"]

        if not packagerepo.is_valid_repo_name(repo_name):
            return "Error: invalid repo name: {}".format(repo_name)

        if repo_name == "main":
            return "Error: repo named \"main\" is reserved"

        if repo_name in os.listdir(PKG_REPO_DIR):
            return "Error: a repo by the name \"{}\" already exists".format(repo_name)

        "repo.{}={}".format(repo_name, repo_url)

    @auth.authorize(groups=["admins"])
    def list_repos(self, msg, matches):
        repos = self._get_repos_from_config()
        if not repos:
            self.respond_to_msg(msg, "Warning: no repos found in config")
            return

        self.respond_to_msg(msg, '\n'.join(['{}: {}'.format(repo_name, pkg_name) for repo_name, pkg_name in self._get_repos_from_config().items()]))
 
    def reload_plugins(self):
        self.plugin_manager.collectPlugins()
        return "Plugins reloaded"


