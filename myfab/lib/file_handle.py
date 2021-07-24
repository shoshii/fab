from jinja2 import Environment, FileSystemLoader
import os

def template_dir():
    return Environment(
        loader=FileSystemLoader(
            ('{}/../template/'.format(os.path.dirname(__file__))),
            encoding="utf-8"
        )
    )