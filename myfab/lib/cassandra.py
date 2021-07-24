from jinja2 import Environment, FileSystemLoader
import os
import json

CONF_DIR = '{}/../conf/'.format(os.path.dirname(__file__))
def get_cluster_json(name):
    with open('{}/{}'.format(CONF_DIR, name), 'r') as f:
        cluster = json.load(f)
    return cluster

def _template_dir():
    return Environment(
        loader=FileSystemLoader(
            ('{}/../template/'.format(os.path.dirname(__file__))),
            encoding="utf-8"
        )
    )
    
def generate_yaml_from_template(**kwargs):
    env = _template_dir()
    template = env.get_template("cassandra.yaml")

    out = template.render({
        'cluster_name': kwargs.get('cluster_name', 'cluster1'),
        'num_tokens': kwargs.get('num_tokens', '16'),
        'endpoint_snitch': kwargs.get('endpoint_snitch', 'GossipingPropertyFileSnitch'),
        'listen_address': kwargs['nodeip'],
        'rpc_address': kwargs['nodeip'],
        'seeds': kwargs['seeds']
    })
    return out

def generate_rackdc_properties_from_template(**kwargs):
    env = _template_dir()
    template = env.get_template("cassandra-rackdc.properties")

    out = template.render({
        'dc': kwargs['dc'],
        'rack': kwargs['rack']
    })
    return out