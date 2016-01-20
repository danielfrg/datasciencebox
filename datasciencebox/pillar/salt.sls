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
        - cloudera.manager.server
        - cloudera.manager.agent
        - hdfs.namenode
        - hive.metastore
        - impala.state-store
    compute:
      roles:
        - salt.minion
        - mesos.slave
        - cloudera.manager.agent
        - hdfs.datanode
        - impala.server
