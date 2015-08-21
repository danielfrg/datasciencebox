{%- from 'spark/settings.sls' import version with context -%}

include:
  - spark

spark-hdfs-1:
  cmd.run:
    - name: hadoop fs -mkdir /spark
    - user: hdfs
    - unless: hadoop fs -test -e /spark

spark-hdfs-2:
  cmd.run:
    - name: tar czf /tmp/{{ version }}.tgz /usr/lib/spark;
    - user: hdfs
    - unless: test -e /tmp/{{ version }}.tgz
    - watch:
      - cmd: spark-hdfs-1

spark-hdfs-3:
  cmd.run:
    - name: hadoop fs -put /tmp/{{ version }}.tgz /spark;
    - user: hdfs
    - unless: hadoop fs -test -e /spark/{{ version }}.tgz
    - watch:
      - cmd: spark-hdfs-2

/usr/lib/spark/conf/spark-env.sh:
  file.managed:
    - source: salt://mesos/spark/spark-env.sh
    - template: jinja
    - user: root
    - group: root
    - require:
      - sls: spark
