from invoke import Collection
from fabric import task, Connection

from myfab.lib.prometheus import generate_yaml_from_template
from myfab.lib.file_handle import get_json
from myfab import docker

from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


@task
def create(c, version='4.0.1'):
    """create prometheus container and volumes args:version"""
    logger.debug('pull prometheus image on {}'.format(c.host))
    c.run('docker pull shoshii/prometheus-centos:{}'.format(version))

    #logger.debug('create prometheus-data volume on {}'.format(c.host))
    #c.run('docker volume create prometheus-data')

    #logger.debug('create prometheus-log volume on {}'.format(c.host))
    #c.run('docker volume create prometheus-log')
    
    logger.debug('create prometheus container on {}'.format(c.host))
    c.run('docker create --net=host \
        --name=prometheus shoshii/prometheus-centos:{}'.format(version))


@task
def rm(c):
    """remove prometheus container and volumes args:"""
    try:
        stop(c)
    except:
        pass
    container_id = get_cid(c)
    if container_id is None:
        raise Exception('no prometheus container on {}'.format(c.host))
    logger.debug('remove prometheus container id:{} on {}'.format(container_id, c.host))
    c.run('docker rm {}'.format(container_id))

    logger.debug('remove prometheus-data volume on {}'.format(c.host))
    #c.run('docker volume remove prometheus-data')

    logger.debug('create prometheus-log volume on {}'.format(c.host))
    #c.run('docker volume remove prometheus-log')


@task
def start(c):
    """start prometheus container args:"""
    logger.info('start prometheus on {}'.format(c.host))
    tmp_dir = '.myfab'
    fname = 'prometheus.yaml'
    yaml_out = generate_yaml_from_template()
    _path = "{}/{}".format(tmp_dir, fname)
    with open(_path, "w", encoding="utf-8") as fw:
        fw.write(yaml_out)
    c.put(_path)
    c.run('docker volume create prometheus-data')
    c.run('docker run --name prometheus --rm -d --net=host -v prometheus-data:/prometheus -v {}:/etc/prometheus/{} prom/prometheus'.format(fname, fname))


@task
def stop(c):
    """stop prometheus container args:"""
    logger.info('stop prometheus on {}'.format(c.host))
    docker.stop(c, 'prometheus')



prometheus_ns = Collection('prometheus')
prometheus_ns.add_task(start, 'start')
prometheus_ns.add_task(stop, 'stop')
prometheus_ns.add_task(rm, 'rm')
