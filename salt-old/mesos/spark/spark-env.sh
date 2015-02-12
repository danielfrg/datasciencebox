export MESOS_NATIVE_LIBRARY=/usr/local/lib/libmesos.so
export SPARK_EXECUTOR_URI=hdfs://{{ namenode }}:8020/{{ hdfs_spark_path }}
export MASTER=zk://{{ zookeeper }}:2181/mesos
