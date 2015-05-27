import shutil
from subprocess import Popen
from tempfile import TemporaryFile

GIT_BIN=shutil.which("git")

class GitStatus:
    def __init__(self, exit_status, stdout, stderr):
        self.exit_status = exit_status
        self.stdout = stdout
        seld.stderr = stderr

def clone(cwd, repository, directory):
    args = [self.git_bin, "clone", "--", repository, directory]

    out, err = TemporaryFile(), TemporaryFile()
    p = Popen(args, cwd=cwd, stdout=out, stderr=err)
    status = p.wait()

    out.seek(0)
    err.seek(0)

    return GitResponse(status, out.read().decode('utf-8'), err.read().decode('utf-8'))

if __name__ == "__main__":
    print("it works")    
