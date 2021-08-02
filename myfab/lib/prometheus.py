import os
import json
from myfab.lib.file_handle import template_dir


def generate_yaml_from_template(**kwargs):
    env = template_dir('prometheus')
    template = env.get_template("prometheus.yml")

    out = template.render()
    return out