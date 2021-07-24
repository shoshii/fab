from invoke import Collection
from fabric.main import Fab
from fabric import Config, Executor
from .cassandra import cassandra_ns

__VERSION__='0.1.0'
ns = Collection()
ns.add_collection(cassandra_ns)
app = Fab(
    version=__VERSION__,
    namespace=ns,
    config_class=Config,
    executor_class=Executor
)

if __name__ == '__main__':
    app.update_config()
    app.run()
