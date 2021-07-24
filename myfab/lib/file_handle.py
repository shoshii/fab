from jinja2 import Environment, FileSystemLoader
import os
import json

def get_json(path):
    with open(path, 'r') as f:
        _json = json.load(f)
    return _json

def template_dir():
    return Environment(
        loader=FileSystemLoader(
            ('{}/../template/'.format(os.path.dirname(__file__))),
            encoding="utf-8"
        )
    )