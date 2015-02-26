include:
  - cdh5.spark
  - cdh5.hdfs.namenode

spark-hdfs-1:
  cmd.run:
    - name: hadoop fs -mkdir /spark
    - user: hdfs
    - unless: hadoop fs -test -e /spark
    - require:
      - sls: cdh5.hdfs.namenode

spark-hdfs-2:
  cmd.run:
    - name: tar czf /tmp/spark.tgz /usr/lib/spark;
    - user: hdfs
    - unless: hadoop fs -test -e /spark/spark.tgz || test -e /tmp/spark.tgz
    - require:
      - cmd: spark-hdfs-1

spark-hdfs-3:
  cmd.run:
    - name: hadoop fs -put /tmp/spark.tgz /spark;
    - user: hdfs
    - unless: hadoop fs -test -e /spark/spark.tgz
    - require:
      - cmd: spark-hdfs-2

/usr/lib/spark/conf/spark-env.sh:
  file.managed:
    - source: salt://mesos/spark/spark-env.sh
    - template: jinja
    - user: root
    - group: root
    - require:
      - sls: cdh5.spark
