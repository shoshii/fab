from invoke import Collection
from fabric import task


@task
def docker(c):
    """install and setup docker args:"""
    c.sudo('yum install -y yum-utils device-mapper-persistent-data lvm2')
    c.sudo('yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo')
    c.sudo('yum install -y docker-ce docker-ce-cli containerd.io')
    try:
        c.sudo('usermod -aG docker {}'.format(c.user))
    except:
        pass
    c.run('newgrp docker &')

    c.sudo('systemctl start docker')
    c.sudo('systemctl enable docker')


centos_ns = Collection('centos')
centos_ns.add_task(docker, 'docker')