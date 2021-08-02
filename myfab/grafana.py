from invoke import Collection
from fabric import task, Connection
from myfab import docker

from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


def get_cid(c):
    return docker.get_containerid(c, 'grafana')

@task
def rm(c):
    """remove grafana container and volumes args:"""
    try:
        stop(c)
    except:
        pass
    container_id = get_cid(c)
    if container_id is None:
        raise Exception('no grafana container on {}'.format(c.host))
    logger.debug('remove grafana container id:{} on {}'.format(container_id, c.host))
    c.run('docker rm {}'.format(container_id))

    logger.debug('remove grafana-data volume on {}'.format(c.host))
    #c.run('docker volume remove grafana-data')


@task
def start(c):
    """start grafana container args:"""
    logger.info('start grafana on {}'.format(c.host))
    tmp_dir = '.myfab'
    c.run('docker volume create grafana-data')
    c.run('docker run --name grafana --rm -d --net=host -v grafana-data:/var/lib/grafana grafana/grafana')


@task
def stop(c):
    """stop grafana container args:"""
    logger.info('stop grafana on {}'.format(c.host))
    docker.stop(c, 'grafana')


grafana_ns = Collection('grafana')
grafana_ns.add_task(start, 'start')
grafana_ns.add_task(stop, 'stop')
grafana_ns.add_task(rm, 'rm')
