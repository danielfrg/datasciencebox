{%- from 'spark/settings.sls' import version with context %}
{%- from 'mesos/settings.sls' import master_fqdn with context %}
{%- from 'cdh5/settings.sls' import namenode_fqdn with context %}

include:
  - spark
  - mesos.conf

spark-hdfs:
  cmd.run:
    - name: |
        cp -r /usr/lib/spark /tmp/{{ version }};
        tar czf /tmp/{{ version }}.tgz /tmp/{{ version }};
        hadoop fs -put /tmp/{{ version }}.tgz /tmp;
    - user: hdfs
    - unless: hadoop fs -test -e /tmp/{{ version }}.tgz
    - require:
      - sls: spark

/usr/lib/spark/conf/spark-env.sh:
  file.managed:
    - source: salt://mesos/spark/spark-env.sh
    - template: jinja
    - user: root
    - group: root
    - context:
      namenode: {{ namenode_fqdn }}
      hdfs_spark_path: /tmp/{{ version }}.tgz
      zookeeper: {{ master_fqdn }}
    - require:
      - sls: spark
