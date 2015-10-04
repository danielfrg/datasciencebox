salt:
  master:
    ip: 'head'

  minion:
    head:
      roles:
        - salt.master
        - salt.minion
        - zookeeper.server
        - mesos.master
        - hdfs.namenode
        - hive.metastore
        - impala.state-store
    compute:
      roles:
        - salt.minion
        - mesos.slave
        - hdfs.datanode
        - impala.server
