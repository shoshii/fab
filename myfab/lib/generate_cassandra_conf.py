from jinja2 import Environment, FileSystemLoader
import os
import argparse

def generate_node_image(**kwargs):
    dir_path = './conf/'
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    env = Environment(loader=FileSystemLoader(("./template"),encoding="utf-8"))

    # create conf/cassandra.yaml
    template = env.get_template("cassandra.yaml")

    out = template.render({
        'cluster_name': kwargs.get('cluster_name', 'cluster1'),
        'num_tokens': kwargs.get('num_tokens', '16'),
        'endpoint_snitch': kwargs.get('endpoint_snitch', 'GossipingPropertyFileSnitch'),
        'listen_address': kwargs['nodeip'],
        'rpc_address': kwargs['nodeip'],
        'seeds': kwargs['seeds']
    })

    with open("{}/cassandra.yaml".format(dir_path), "w", encoding="utf-8") as fw:
        fw.write(out)

    # create conf/cassandra-rackdc.properties
    template = env.get_template("cassandra-rackdc.properties")

    out = template.render({
        'dc': kwargs['dc'],
        'rack': kwargs['rack']
    })

    with open("{}/cassandra-rackdc.properties".format(dir_path), "w", encoding="utf-8") as fw:
        fw.write(out)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("nodeip", type=str)
    parser.add_argument("seeds", type=str)
    parser.add_argument("--dc", type=str)
    parser.add_argument("--rack", type=str)
    args = parser.parse_args()
    generate_node_image(nodeip=args.nodeip, seeds=args.seeds, dc=args.dc, rack=args.rack)