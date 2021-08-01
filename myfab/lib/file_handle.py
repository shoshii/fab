from jinja2 import Environment, FileSystemLoader
import os
import json
import shutil

def get_json(path):
    with open(path, 'r') as f:
        _json = json.load(f)
    return _json

def template_dir(name):
    return Environment(
        loader=FileSystemLoader(
            ('{}/../template/{}/'.format(os.path.dirname(__file__), name)),
            encoding="utf-8"
        )
    )

def upload_file(src_file_name, dest_path):
    shutil.copy2(
        '{}/../file/{}'.format(os.path.dirname(__file__), src_file_name),
        dest_path
    )