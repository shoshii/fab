from invoke import Collection
from fabric.main import Fab
from fabric import Config, Executor
from .cassandra import cassandra_ns
from .docker import docker_ns
from .centos import centos_ns
from .version import __VERSION__

ns = Collection()
ns.add_collection(cassandra_ns)
ns.add_collection(docker_ns)
ns.add_collection(centos_ns)

app = Fab(
    version=__VERSION__,
    namespace=ns,
    config_class=Config,
    executor_class=Executor
)

if __name__ == '__main__':
    app.update_config()
    app.run()
