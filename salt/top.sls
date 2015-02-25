base:
  'roles:salt.master':
    - match: grain
    - salt.master

  'roles:miniconda':
    - match: grain
    - miniconda

  'roles:ipython.notebook':
    - match: grain
    - ipython.notebook

  'roles:zookeeper':
    - match: grain
    - cdh5.zookeeper

  'roles:mesos.master':
    - match: grain
    - mesos.master

  'roles:mesos.slave':
    - match: grain
    - mesos.slave

  'roles:spark':
    - match: grain
    - spark
    - mesos.spark

  'roles:namenode':
    - match: grain
    - cdh5.hdfs.namenode
    - cdh5.hdfs.users

  'roles:datanode':
    - match: grain
    - cdh5.hdfs.datanode
