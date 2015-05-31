import re
import unittest
import json

def is_valid_repo_name(name):
    expr = "[\w-]{2,255}"
    return type(name) is str and re.fullmatch(expr, name) and name.islower() and name[0].isalpha()

class PackageRepo:
    def __init__(self, name, url, data):
        if not is_valid_repo_name(name):
           raise "Invalid repo name: {}".format(name) 
        self.name = name
        self.url = url
        self.data = json.load(data)

