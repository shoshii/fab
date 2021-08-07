from invoke import Collection
from fabric import task


from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


def get_containerid(c, name):
    """get containerid args: name"""
    id = c.run(
        'docker ps -a | grep {} | tail -n 1 | cut -d " " -f 1'.format(name),
        hide=True
    ).stdout.strip()
    if id is None or id == '':
        return None
    return id


@task
def start(c, name, *args):
    """start docker container args: name"""
    container_id = get_containerid(c, name)
    str_args = ' '.join(args)
    c.run('docker start {} {}'.format(container_id, str_args))


@task
def stop(c, name):
    """stop docker container args: name"""
    container_id = get_containerid(c, name)
    if container_id is None:
        raise Exception('no container with name of "{}" on {}'.format(name, c.host))
    logger.debug('docker stop container_id:{}'.format(container_id))
    c.run('docker stop {}'.format(container_id))


@task
def rm(c, name):
    """remove docker container args: name"""
    container_id = get_containerid(c)
    if container_id is None:
        raise Exception('no container with name of "{}" on {}'.format(name, c.host))
    try:
        stop(c, name)
    except:
        pass
    c.run('docker rm {}'.format(container_id))


@task
def exec(c, name, cmd='uname'):
    """execute command args:name, cmd"""
    container_id = get_containerid(c, name)
    c.run('docker exec -i {} {}'.format(container_id, cmd))


docker_ns = Collection('docker')
docker_ns.add_task(start, 'start')
docker_ns.add_task(stop, 'stop')
docker_ns.add_task(rm, 'rm')
docker_ns.add_task(exec, 'exec')
