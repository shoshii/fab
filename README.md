myfab
===

Apache Cassandra や Prometheusの構築、運用タスクを実行できるfabricツールです。

## install

```
$ pip install .
```

## how to use

```
$ myfab -l
Subcommands:

  cassandra.cluster   create cluster args:conf, start='0'
  cassandra.config    config node args:conf
  cassandra.create    create cassandra container and volumes args:version
  cassandra.exec      execute command args: cmd
  cassandra.rm        remove cassandra container and volumes args:
  cassandra.start     start cassandra container args:
  cassandra.stop      stop cassandra container args:
  centos.docker       install and setup docker args:
  docker.exec         execute command args:name, cmd
  docker.rm           remove docker container args: name
  docker.start        start docker container args: name
  docker.stop         stop docker container args: name
  grafana.rm          remove grafana container and volumes args:
  grafana.start       start grafana container args:
  grafana.stop        stop grafana container args:
  prometheus.config
  prometheus.create   create prometheus container and volumes args:version
  prometheus.rm       remove prometheus container and volumes args:
  prometheus.start    start prometheus container args:
  prometheus.stop     stop prometheus container args:
```

### 参考

* [Cassandra開発環境構築](https://qiita.com/shoshii/items/a733b7534638606209bf)
* [Cassandra rpmパッケージ作成](https://qiita.com/shoshii/items/4a620aa53ce6fa1a6bf9)

