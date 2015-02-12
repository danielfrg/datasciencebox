{%- from 'cdh5/settings.sls' import namenode_dirs with context %}

include:
  - java
  - cdh5
  - cdh5.hadoop.conf

hadoop-hdfs-namenode:
  pkg.installed:
    - require:
      - sls: cdh5

{% for dir in namenode_dirs %}
{{ dir }}:
  file.directory:
    - makedirs: true
    - user: hdfs
    - mode: 700
{% endfor %}

# This is dangeours anyways
format-hdfs:
  cmd.run:
    - name: sudo -u hdfs hdfs namenode -format > /etc/hadoop/conf/hdfs-format-check-dont-delele.log
    - unless: test -e /etc/hadoop/conf/hdfs-format-check-dont-delele.log
    - require:
      - pkg: hadoop-hdfs-namenode
      - sls: cdh5.hadoop.conf
      {% for dir in namenode_dirs %}
      - file: {{ dir }}
      {% endfor %}

start-hadoop-hdfs-namenode:
  service.running:
    - name: hadoop-hdfs-namenode
    - enable: true
    - require:
      - cmd: format-hdfs
