import unittest
from tempfile import TemporaryDirectory
from os.path import join, exists
from urllib.parse import urlparse

import telex.git as git

REPO_URL = "https://github.com/datamachine/telegram-pybot-dice.git"
REPO_NAME = "dice"
REPO_DEFAULT_NAME="telegram-pybot-dice"
REPO_BARE_NAME="telegram-pybot-dice.git"

class GetDefaultRepoDirnameTest(unittest.TestCase):
    def test_default(self):
        self.assertEqual(git.get_default_repo_dirname("https://github.com/datamachine/telegram-pybot-dice.git"), "telegram-pybot-dice")
        self.assertEqual(git.get_default_repo_dirname("https://github.com/datamachine/telegram-pybot-dice"), "telegram-pybot-dice")
        self.assertEqual(git.get_default_repo_dirname("git@github.com:datamachine/telegram-pybot-dice.git"), "telegram-pybot-dice")

    def test_default_bare(self):
        self.assertEqual(git.get_default_repo_dirname("https://github.com/datamachine/telegram-pybot-dice.git", bare=True), "telegram-pybot-dice.git")
        self.assertEqual(git.get_default_repo_dirname("https://github.com/datamachine/telegram-pybot-dice", bare=True), "telegram-pybot-dice.git")
        self.assertEqual(git.get_default_repo_dirname("git@github.com:datamachine/telegram-pybot-dice.git", bare=True), "telegram-pybot-dice.git")

class CloneTest(unittest.TestCase):
    def test_clone_to_empty_with_default_name(self):
        with TemporaryDirectory() as d:
            # clone into sdefault directory
            gs = git.clone(REPO_URL, cwd=d, directory=None)
            self.assertIsNotNone(gs)
            self.assertTrue(exists(join(d, REPO_DEFAULT_NAME, ".git")))
            self.assertEqual(gs.exit_status, 0)
        
    def test_clone_to_empty_with_name(self):
        with TemporaryDirectory() as d:
            # clone into specified directory
            gs = git.clone(REPO_URL, cwd=d, directory=REPO_NAME)
            self.assertIsNotNone(gs)
            self.assertTrue(exists(join(d, REPO_NAME, ".git")))
            self.assertEqual(gs.exit_status, 0)

class PullTest(unittest.TestCase):
    def test_pull_up_to_date(self):
        with TemporaryDirectory() as d:
            # clone repo
            gs = git.clone(REPO_URL, cwd=d, directory=REPO_NAME)
            self.assertIsNotNone(gs)
            self.assertTrue(exists(join(d, REPO_NAME, ".git")))
            self.assertEqual(gs.exit_status, 0)

            # pull while on latest revision
            gs = git.pull(cwd=join(d, REPO_NAME))
            self.assertIsNotNone(gs)
            self.assertEqual(gs.exit_status, 0)
        
    def test_pull_out_of_date(self):
        with TemporaryDirectory() as d:
            # Clone a repo
            gs = git.clone(REPO_URL, cwd=d, directory=REPO_NAME)
            self.assertIsNotNone(gs)
            self.assertEqual(gs.exit_status, 0)

            # Revert to the initial commit
            gs = git.reset(cwd=join(d, REPO_NAME), hard=True, commit="6f72f1ad1589f73d62165e19df873c59e829e1dd")
            self.assertIsNotNone(gs)
            self.assertEqual(gs.exit_status, 0)

            # Use pull to get update to the latest commit
            gs = git.pull(cwd=join(d, REPO_NAME))
            self.assertIsNotNone(gs)
            self.assertEqual(gs.exit_status, 0)

if __name__ == "__main__":
    unittest.main()

