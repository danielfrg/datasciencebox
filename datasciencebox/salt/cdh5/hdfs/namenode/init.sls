{%- from 'cdh5/hdfs/settings.sls' import namenode_dirs with context %}

include:
  - java
  - cdh5.repo
  - cdh5.hdfs

hadoop-hdfs-namenode:
  pkg.installed:
    - require:
      - sls: cdh5.repo

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
      - sls: cdh5.hdfs
      {% for dir in namenode_dirs %}
      - file: {{ dir }}
      {% endfor %}

start-hadoop-hdfs-namenode:
  service.running:
    - name: hadoop-hdfs-namenode
    - enable: true
    - watch:
      - cmd: format-hdfs
      - sls: cdh5.hdfs
      {% for dir in namenode_dirs %}
      - file: {{ dir }}
      {% endfor %}

hdfs-tmp-create:
  cmd.run:
    - name: hadoop fs -mkdir /tmp
    - user: hdfs
    - unless: hadoop fs -ls /tmp
    - require:
        - service: start-hadoop-hdfs-namenode

hdfs-tmp-permission:
  cmd.wait:
    - name: hadoop fs -chmod -R 1777 /tmp
    - user: hdfs
    - watch:
        - cmd: hdfs-tmp-create
