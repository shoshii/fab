from invoke import Collection
from fabric import task, Connection
import time, json
from myfab.lib.generate_cassandra_conf import generate_node_image

def get_c_containerid(c):
    return c.run('docker ps -a | grep cassandra | tail -n 1 | cut -d " " -f 1', hide=True).stdout.strip()

@task
def create(c, version='4.0.1'):
    c.run('docker pull shoshii/cassandra-centos:{}'.format(version))
    c.run('docker volume create cassandra-data')
    c.run('docker volume create cassandra-log')
    
    c.run('docker create --net=host -v cassandra-data:/var/lib/cassandra -v cassandra-log:/var/log/cassandra --name=cassandra shoshii/cassandra-centos:{}'.format(version))


@task
def start(c):
    """start cassandra container"""
    container_id = get_c_containerid(c)
    c.run('docker start {}'.format(container_id))

@task
def stop(c):
    """stop cassandra container"""
    container_id = get_c_containerid(c)
    c.run('docker stop {}'.format(container_id))

@task
def rm(c):
    container_id = get_c_containerid(c)
    try:
        stop(c)
    except:
        pass
    c.run('docker rm {}'.format(container_id))
    c.run('docker volume remove cassandra-data')
    c.run('docker volume remove cassandra-log')


@task
def exec(c, cmd='uname'):
    """execute command"""
    container_id = get_c_containerid(c)
    c.run('docker exec -i {} {}'.format(container_id, cmd))

@task
def cluster(c, name='cluster1', start='0'):
    """create cluster"""
    cluster = None
    with open('./conf/{}.json'.format(name), 'r') as f:
        cluster = json.load(f)
    seeds = cluster['seeds']
    cluster_name = cluster['cluster_name']
    nodes = cluster['nodes']
    for key, value in nodes.items():
        print('key:{}, value:{}, cluster_name:{}, seeds:{}'.format(key, value, cluster_name, seeds))
        c = Connection(key)
        try:
            rm(c)
        except:
            pass
        create(c)
        container_id = get_c_containerid(c)
        generate_node_image(
            nodeip=key,
            cluster_name=cluster_name,
            seeds=seeds,
            dc=value['dc'],
            rack=value['rack']
        )
        c.put('conf/cassandra.yaml')
        c.put('conf/cassandra-rackdc.properties')
        c.run('docker cp cassandra.yaml {}:/etc/cassandra/conf/'.format(container_id))
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
