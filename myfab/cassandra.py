from invoke import Collection
from fabric import task, Connection
import time
import os
import stat
import subprocess
from myfab.lib.cassandra import generate_yaml_from_template, \
                                generate_rackdc_properties_from_template, \
                                generate_cassandra_envsh_from_template
from myfab.lib.file_handle import get_json, upload_file
from myfab import docker

from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

def get_cid(c):
    return docker.get_containerid(c, 'cassandra')

def get_alive_nodes_ips(conf):
    """get UN nodes IP list"""
    cluster = get_json(conf)
    cluster_name = cluster['cluster_name']
    nodes = cluster['nodes']
    seeds = []
    for node_ip in nodes.keys():
        logger.debug('nodetool status -h {}'.format(node_ip))
        p1 = subprocess.Popen([
            'nodetool', '-h', node_ip, '-u', 'cassandra', '-pw', 'cassandra', 'status'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8')
        p2 = subprocess.Popen(
            ['grep', '-e', '^UN'],
            stdin=p1.stdout, stdout=subprocess.PIPE, encoding='utf8')
        p3 = subprocess.Popen(
            ['sed', 's/[\t ]\+/\t/g'],
            stdin=p2.stdout, stdout=subprocess.PIPE, encoding='utf8')
        p4 = subprocess.Popen(
            ['cut', '-f', '2'],
            stdin=p3.stdout, stdout=subprocess.PIPE, encoding='utf8')
        
        #output = p3.communicate()[0]
        res = p4.communicate()[0]
        logger.debug('output:{}'.format(res))
        if res == '':
            logger.warning('no UN nodes')
            continue
        else:
            seeds = res.split("\n")
            break
    return seeds


@task
def create(c, version='4.0.1'):
    """create cassandra container and volumes args:version"""
    logger.debug('pull cassandra image on {}'.format(c.host))
    c.run('docker pull shoshii/cassandra-centos:{}'.format(version))

    logger.debug('create cassandra-data volume on {}'.format(c.host))
    c.run('docker volume create cassandra-data')

    logger.debug('create cassandra-log volume on {}'.format(c.host))
    c.run('docker volume create cassandra-log')
    
    logger.debug('create cassandra container on {}'.format(c.host))
    c.run('docker create -e TZ=Asia/Tokyo --net=host \
        -v cassandra-log:/usr/share/cassandra/logs -v cassandra-data:/var/lib/cassandra \
        --name=cassandra shoshii/cassandra-centos:{}'.format(version))


@task
def start(c):
    """start cassandra container args:"""
    logger.info('start cassandra on {}'.format(c.host))
    docker.start(c, 'cassandra')
    max_retry = 20
    while True:
        time.sleep(10)
        p1 = subprocess.Popen([
            'nodetool', '-h', c.host, '-u', 'cassandra', '-pw', 'cassandra', 'status'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8')
        p2 = subprocess.Popen(['grep', c.host], stdin=p1.stdout, stdout=subprocess.PIPE, encoding='utf8')
        p3 = subprocess.Popen(['cut', '-d', ' ', '-f', '1'], stdin=p2.stdout, stdout=subprocess.PIPE, encoding='utf8')
        output = p3.communicate()[0]
        output = output.strip()
        logger.debug('nodetool status output:{}'.format(output))
        if p3.returncode != 0 or output != 'UN':
            logger.info('nodetool status failed or status is not UN')
            max_retry -= 1
            if max_retry == 0:
                logger.warning('retry failed')
                exit(1)
            continue
        logger.info('cassandra start ok')
        break



@task
def stop(c):
    """stop cassandra container args:"""
    logger.info('stop cassandra on {}'.format(c.host))
    docker.stop(c, 'cassandra')


@task
def rm(c, rm_volume=False):
    """remove cassandra container and volumes args:"""
    try:
        stop(c)
    except:
        pass
    container_id = get_cid(c)
    if container_id is None:
        raise Exception('no cassandra container on {}'.format(c.host))
    logger.debug('remove cassandra container id:{} on {}'.format(container_id, c.host))
    c.run('docker rm {}'.format(container_id))

    if rm_volume:
        logger.debug('remove cassandra-data volume on {}'.format(c.host))
        c.run('docker volume remove cassandra-data')

        logger.debug('create cassandra-log volume on {}'.format(c.host))
        c.run('docker volume remove cassandra-log')


@task
def exec(c, cmd='uname'):
    """execute command args: cmd"""
    logger.info('execute command {} on {}'.format(cmd, c.host))
    docker.exec(c, name='cassandra', cmd=cmd)


@task
def config(c, conf):
    """config node args:conf"""
    logger.info('start configuring cassandra on {}'.format(c.host))
    alive_ips = get_alive_nodes_ips(conf)
    if len(alive_ips) == 0:
        seeds = '{}:7000'.format(c.host)
    else:
        seeds = '{}:7000'.format(alive_ips[0])
    logger.info('set seeds as {}'.format(seeds))

    cluster = get_json(conf)
    cluster_name = cluster['cluster_name']
    node = cluster['nodes'][c.host]
    tmp_dir = '.myfab'
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    
    container_id = get_cid(c)

    # cassandra.yaml
    fname = 'cassandra.yaml'
    yaml_out = generate_yaml_from_template(
        nodeip=c.host,
        cluster_name=cluster_name,
        seeds=seeds
    )
    _path = "{}/{}".format(tmp_dir, fname)
    with open(_path, "w", encoding="utf-8") as fw:
        fw.write(yaml_out)
    c.put(_path)
    c.run('docker cp {} {}:/etc/cassandra/conf/'.format(fname, container_id))
    logger.info('uploaded {} to container:{}'.format(fname, container_id))

    # cassandra-rackdc.properties
    fname = 'cassandra-rackdc.properties'
    rackdc_out = generate_rackdc_properties_from_template(
        dc=node['dc'],
        rack=node['rack']
    )
    _path = "{}/{}".format(tmp_dir, fname)
    with open(_path, "w", encoding="utf-8") as fw:
        fw.write(rackdc_out)
    c.put(_path)
    c.run('docker cp {} {}:/etc/cassandra/conf/'.format(fname, container_id))
    logger.info('uploaded {} to container:{}'.format(fname, container_id))

    # cassandra-env.sh
    fname = 'cassandra-env.sh'
    exporter_name = 'cassandra-exporter-agent-0.9.10.jar'
    _path = "{}/{}".format(tmp_dir, fname)
    env_out = generate_cassandra_envsh_from_template(
        rmi_server_hostname= c.host,
        cassandra_exporter_agent_filename = exporter_name
    )
    with open(_path, "w", encoding="utf-8") as fw:
        fw.write(env_out)
    st = os.stat(_path)
    os.chmod(_path, st.st_mode | stat.S_IEXEC)
    c.put(_path)
    c.run('docker cp {} {}:/etc/cassandra/conf/'.format(fname, container_id))
    logger.info('uploaded {} to container:{}'.format(fname, container_id))

    # cassandra-exporter-agent-0.9.10.jar
    """
    _path = "{}/{}".format(tmp_dir, exporter_name)
    upload_file(src_file_name='cassandra/{}'.format(exporter_name), dest_path=_path)
    c.put(_path)
    c.run('docker cp {} {}:/usr/share/cassandra/lib/'.format(exporter_name, container_id))
    logger.info('uploaded {} to container:{}'.format(exporter_name, container_id))
    """
    
    logger.info('config ok to container:{}'.format(container_id))


@task
def cluster(c, conf, with_replace='0'):
    """create cluster args:conf, start='0'"""
    cluster = get_json(conf)
    nodes = cluster['nodes']

    for key, value in nodes.items():
        logger.debug('setting start on the node: key:{}, value:{}'.format(key, value))
        c = Connection(key)
        if int(with_replace) == 1:
            try:
                rm(c)
            except:
                pass
            create(c)
        config(c, conf)
        start(c)


cassandra_ns = Collection('cassandra')
cassandra_ns.add_task(create, 'create')
cassandra_ns.add_task(config, 'config')
cassandra_ns.add_task(start, 'start')
cassandra_ns.add_task(stop, 'stop')
cassandra_ns.add_task(rm, 'rm')
cassandra_ns.add_task(exec, 'exec')
cassandra_ns.add_task(cluster, 'cluster')