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

@task
def java(c):
    """install and setup java args:"""
    c.sudo("yum install -y wget java-1.8.0-openjdk")

@task
def dlhadoop(c):
    """download hadoop args:"""
    c.sudo("yum install -y wget")
    version = 'hadoop-3.3.2'
    try:
        c.run("ls %s.tar.gz || wget http://ftp.jaist.ac.jp/pub/apache/hadoop/common/%s/%s.tar.gz" % (version, version, version))
        c.run("ls %s.tar.gz && tar zxfv %s.tar.gz" % (version, version))
        c.sudo("mv %s /usr/local/" % version)
    except:
        pass
    c.sudo("chown -R root:root /usr/local/%s" % version)
    try:
        c.sudo("sed -i -e 's|# export JAVA_HOME=|export JAVA_HOME=/usr/lib/jvm/jre-1.8.0-openjdk|g' /usr/local/%s/etc/hadoop/hadoop-env.sh" % version)
        c.sudo("mkdir -p /var/hadoop/dfs/{jn,nn,dn}")
    except:
        pass

centos_ns = Collection('centos')
centos_ns.add_task(docker, 'docker')
centos_ns.add_task(java, 'java')
centos_ns.add_task(dlhadoop, 'dlhadoop')
