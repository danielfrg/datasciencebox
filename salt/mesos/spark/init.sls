include:
  - spark

spark-hdfs-1:
  cmd.run:
    - name: hadoop fs -mkdir /spark
    - user: hdfs
    - unless: hadoop fs -test -e /spark

spark-hdfs-2:
  cmd.run:
    - name: tar czf /tmp/spark.tgz /usr/lib/spark;
    - user: hdfs
    - unless: hadoop fs -test -e /spark/spark.tgz || test -e /tmp/spark.tgz
    - require:
      - cmd: spark-hdfs-1

download-spark-force:
  cmd.run:
    - name: wget http://d3kbcqa49mib13.cloudfront.net/spark-1.3.0-bin-hadoop2.4.tgz -q
    - cwd: /tmp
    - unless: test -e /tmp/spark-1.3.0-bin-hadoop2.4.tgz

spark-hdfs-3:
  cmd.run:
    - name: hadoop fs -put /tmp/spark-1.3.0-bin-hadoop2.4.tgz /spark;
    - user: hdfs
    - unless: hadoop fs -test -e /spark/spark.tgz
    - require:
      - cmd: spark-hdfs-2
      - cmd: download-spark-force

/usr/lib/spark/conf/spark-env.sh:
  file.managed:
    - source: salt://mesos/spark/spark-env.sh
    - template: jinja
    - user: root
    - group: root
    - require:
      - sls: spark
