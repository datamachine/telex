import re
import unittest

def is_valid_repo_name(name):
    expr = "[\w-]{2,255}"
    return type(name) is str and re.fullmatch(expr, name) and name.islower() and name[0].isalpha()

class PackageRepo:
    def __init__(self, name, url):
        pass


