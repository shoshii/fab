import os
from invoke import Collection
from fabric import task


@task
def sethosts(c):
    """set /etc/hosts"""
    src_dir = '{}/../myfab/file/centos/'.format(os.path.dirname(__file__))
    _path = "{}/{}".format(src_dir, 'hosts')
    c.put(_path)
    #c.sudo('grep 192.168.100.101 /etc/hosts || sudo echo "192.168.100.101 master1" >> /etc/hosts')
    c.sudo('mv /home/shoshii/hosts /etc/hosts')
    c.sudo('chown root:root /etc/hosts')
    #c.sudo('hostname')

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

ZKVERSION = '3.6.3'
@task
def dlzk(c):
    """download hadoop args:"""
    c.sudo("yum install -y wget")
    version = 'zookeeper-%s' % ZKVERSION
    try:
        c.run("ls apache-%s-bin.tar.gz || wget https://dlcdn.apache.org/zookeeper/%s/apache-%s-bin.tar.gz --no-check-certificate" % (version, version, version))
        c.run("ls apache-%s-bin.tar.gz && tar zxfv apache-%s-bin.tar.gz" % (version, version))
        c.sudo("mv /home/shoshii/apache-%s-bin /usr/local/%s" % (version, version))
    except:
        pass
    c.sudo("chown -R root:root /usr/local/%s" % version)

    src_dir = '{}/../myfab/file/centos/'.format(os.path.dirname(__file__))
    _path = "{}/{}".format(src_dir, 'zoo.cfg')
    c.put(_path)
    c.sudo('mv /home/shoshii/zoo.cfg /usr/local/%s/conf/' % version)
    c.sudo('chown root:root /usr/local/%s/conf/zoo.cfg' % version)

@task
def startzk(c):
    version = 'zookeeper-%s' % ZKVERSION
    c.sudo('/usr/local/%s/bin/zkServer.sh start' % version)
    c.sudo('/usr/local/%s/bin/zkCli.sh -server 127.0.0.1:2181' % version)


centos_ns = Collection('centos')
centos_ns.add_task(sethosts, 'sethosts')
centos_ns.add_task(docker, 'docker')
centos_ns.add_task(java, 'java')
centos_ns.add_task(dlhadoop, 'dlhadoop')
centos_ns.add_task(dlzk, 'dlzk')
centos_ns.add_task(startzk, 'startzk')
