import os
from invoke import Collection
from fabric import task


@task
def python3(c):
    """install python3"""
    c.sudo('apt update')
    c.sudo('apt install -y software-properties-common')
    c.sudo('add-apt-repository ppa:deadsnakes/ppa')
    c.sudo('apt update')
    c.sudo('apt install -y python3.10')
    c.sudo('apt install -y python3-pip')
    

ubuntu_ns = Collection('ubuntu')
ubuntu_ns.add_task(python3, 'python3')
