import shutil
from subprocess import Popen
from tempfile import TemporaryFile
from urllib.parse import urlparse
from pathlib import PurePath
from urllib.parse import unquote

GIT_BIN=shutil.which("git")


# Determine the default directory name used by git for the uri
def get_default_repo_dirname(uri, bare=False):
    path = PurePath(urlparse(uri)[2])
    name = unquote(path.parts[-1])
    if not bare and path.suffix == ".git":
        return name[0:-4]

    if bare and path.suffix != ".git":
        return "{}.git".format(name)

    return name

class GitStatus:
    def __init__(self, exit_status, stdout, stderr):
        self.exit_status = exit_status
        self.stdout = stdout
        self.stderr = stderr

    def success(self):
        return self.exit_status == 0

def clone(repository, directory=None, cwd=None):
    args = [GIT_BIN, "clone", "--", repository]
    if directory: args += [directory]
    
    with TemporaryFile() as outf, TemporaryFile() as errf:
        popen_args = dict(stdout=outf, stderr=errf)
        if cwd:
            popen_args["cwd"] = cwd
        p = Popen(args, **popen_args)
        status = p.wait()

        outf.seek(0)
        errf.seek(0)

        return GitStatus(status, outf.read().decode('utf-8'), errf.read().decode('utf-8'))
    return None

def reset(cwd, hard=False, commit=None):
    args = [GIT_BIN, "reset"]
    if hard: args += ["--hard"]
    if commit: args += [commit]

    with TemporaryFile() as outf, TemporaryFile() as errf:
        p = Popen(args, cwd=cwd, stdout=outf, stderr=errf)
        status = p.wait()

        outf.seek(0)
        errf.seek(0)

        return GitStatus(status, outf.read().decode('utf-8'), errf.read().decode('utf-8'))
    return None

def pull(cwd):
    args = [GIT_BIN, "pull"]

    with TemporaryFile() as outf, TemporaryFile() as errf:
        p = Popen(args, cwd=cwd, stdout=outf, stderr=errf)
        status = p.wait()

        outf.seek(0)
        errf.seek(0)

        return GitStatus(status, outf.read().decode('utf-8'), errf.read().decode('utf-8'))
    return None
