{%- from 'spark/settings.sls' import version with context %}
{%- from 'mesos/settings.sls' import mesos with context %}
{%- from 'cdh5/settings.sls' import namenode_fqdn with context %}

include:
  - spark
  - cdh5.hdfs.namenode

spark-hdfs-1:
  cmd.run:
    - name: cp -r /usr/lib/spark /tmp/{{ version }};
    - user: hdfs
    - unless: hadoop fs -test -e /tmp/{{ version }}.tgz
    - require:
      - sls: spark
      - sls: cdh5.hdfs.namenode

spark-hdfs-2:
  cmd.run:
    - name: tar czf /tmp/{{ version }}.tgz /tmp/{{ version }};
    - user: hdfs
    - unless: hadoop fs -test -e /tmp/{{ version }}.tgz || test -e /tmp/{{ version }}.tgz
    - require:
      - cmd: spark-hdfs-1

spark-hdfs-3:
  cmd.run:
    - name: hadoop fs -put /tmp/{{ version }}.tgz /tmp;
    - user: hdfs
    - unless: hadoop fs -test -e /tmp/{{ version }}.tgz
    - require:
      - cmd: spark-hdfs-2


/usr/lib/spark/conf/spark-env.sh:
  file.managed:
    - source: salt://mesos/spark/spark-env.sh
    - template: jinja
    - user: root
    - group: root
    - context:
      namenode: {{ namenode_fqdn }}
      hdfs_spark_path: /tmp/{{ version }}.tgz
      zookeepers: {{ mesos['connection_string'] }}
    - require:
      - sls: spark
      - sls: cdh5.hdfs.namenode
