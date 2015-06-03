import re
import unittest
from .repo import *

# Unit Tests
class TestRepoNames(unittest.TestCase):
    def test_valid_names(self):
        self.assertTrue(is_valid_repo_name("ex"))
        self.assertTrue(is_valid_repo_name("e-"))
        self.assertTrue(is_valid_repo_name("e_"))
        self.assertTrue(is_valid_repo_name("test"))
        self.assertTrue(is_valid_repo_name("test1"))
        self.assertTrue(is_valid_repo_name("test2-"))
        self.assertTrue(is_valid_repo_name("test-3"))
        self.assertTrue(is_valid_repo_name("te_st-4"))
        self.assertTrue(is_valid_repo_name("test_5-_-"))
        self.assertTrue(is_valid_repo_name("lorem-ipsum-dolor-sit-amet_-consectetur-adipiscing-elit_-quisque-mollis-ex-mauris_-quisque-molestie-metus-ac-nunc-pulvinar-porta_-mauris-orci-libero_-accumsan-et-ornare-sed_-finibus-ac-tortor_-in-laoreet-facilisis-nunc_-vel-mollis-magna-euismod-et-nullam_"))

    def test_invalid_names(self):
        self.assertFalse(is_valid_repo_name(None))
        self.assertFalse(is_valid_repo_name(""))
        self.assertFalse(is_valid_repo_name("a"))
        self.assertFalse(is_valid_repo_name("-"))
        self.assertFalse(is_valid_repo_name("_"))
        self.assertFalse(is_valid_repo_name("."))
        self.assertFalse(is_valid_repo_name("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque mollis ex mauris. Quisque molestie metus ac nunc pulvinar porta. Mauris orci libero, accumsan et ornare sed, finibus ac tortor. In laoreet facilisis nunc, vel mollis magna euismod et nullam."))

if __name__ == "__main__":
    unittest.main()
