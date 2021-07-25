from invoke import Collection
from fabric import task, Connection
import time
import os
from myfab.lib.cassandra import generate_yaml_from_template, \
                                generate_rackdc_properties_from_template
from myfab.lib.file_handle import get_json
from myfab import docker

def get_cid(c):
    return docker.get_containerid(c, 'cassandra')


@task
def create(c, version='4.0.1'):
    """create cassandra container and volumes args:version"""
    c.run('docker pull shoshii/cassandra-centos:{}'.format(version))
    c.run('docker volume create cassandra-data')
    c.run('docker volume create cassandra-log')
    
    c.run('docker create --net=host -v cassandra-data:/var/lib/cassandra -v cassandra-log:/var/log/cassandra --name=cassandra shoshii/cassandra-centos:{}'.format(version))


@task
def start(c):
    """start cassandra container args:"""
    docker.start(c, 'cassandra')


@task
def stop(c):
    """stop cassandra container args:"""
    docker.stop(c, 'cassandra')


@task
def rm(c):
    """remove cassandra container and volumes args:"""
    container_id = get_cid(c)
    try:
        stop(c)
    except:
        pass
    c.run('docker rm {}'.format(container_id))
    c.run('docker volume remove cassandra-data')
    c.run('docker volume remove cassandra-log')


@task
def exec(c, cmd='uname'):
    """execute command args: cmd"""
    docker.exec(c, name='cassandra', cmd=cmd)


@task
def cluster(c, conf, start='0'):
    """create cluster args:conf, start='0'"""
    cluster = get_json(conf)
    seeds = cluster['seeds']
    cluster_name = cluster['cluster_name']
    nodes = cluster['nodes']

    tmp_dir = '.myfab'
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    for key, value in nodes.items():
        print('key:{}, value:{}, cluster_name:{}, seeds:{}'.format(key, value, cluster_name, seeds))
        c = Connection(key)
        try:
            rm(c)
        except:
            pass
        create(c)
        container_id = get_cid(c)
        yaml_out = generate_yaml_from_template(
            nodeip=key,
            cluster_name=cluster_name,
            seeds=seeds
        )
        _path = "{}/cassandra.yaml".format(tmp_dir)
        with open(_path, "w", encoding="utf-8") as fw:
            fw.write(yaml_out)
        c.put(_path)
        c.run('docker cp cassandra.yaml {}:/etc/cassandra/conf/'.format(container_id))

        rackdc_out = generate_rackdc_properties_from_template(
            dc=value['dc'],
            rack=value['rack']
        )
        _path = "{}/cassandra-rackdc.properties".format(tmp_dir)
        with open(_path, "w", encoding="utf-8") as fw:
            fw.write(rackdc_out)
        c.put(_path)
        c.run('docker cp cassandra-rackdc.properties {}:/etc/cassandra/conf/'.format(container_id))

        if int(start) == 1:
            start(c)
            time.sleep(60)


cassandra_ns = Collection('cassandra')
cassandra_ns.add_task(create, 'create')
cassandra_ns.add_task(start, 'start')
cassandra_ns.add_task(stop, 'stop')
cassandra_ns.add_task(rm, 'rm')
cassandra_ns.add_task(exec, 'exec')
cassandra_ns.add_task(cluster, 'cluster')
