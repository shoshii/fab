from invoke import Collection
from fabric import task

def get_containerid(c, name):
    """get containerid args: name"""
    return c.run(
        'docker ps -a | grep {} | tail -n 1 | cut -d " " -f 1'.format(name),
        hide=True
    ).stdout.strip()


@task
def start(c, name):
    """start docker container args: name"""
    container_id = get_containerid(c, name)
    c.run('docker start {}'.format(container_id))


@task
def stop(c, name):
    """stop docker container args: name"""
    container_id = get_containerid(c, name)
    c.run('docker stop {}'.format(container_id))


@task
def rm(c, name):
    """remove docker container args: name"""
    container_id = get_containerid(c)
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
