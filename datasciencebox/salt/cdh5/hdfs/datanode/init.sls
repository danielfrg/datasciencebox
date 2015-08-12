{%- from 'cdh5/settings.sls' import datanode_dirs with context %}

include:
  - cdh5
  - cdh5.hdfs.conf

hadoop-hdfs-datanode:
  pkg.installed:
    - require:
      - sls: cdh5

{% for dir in datanode_dirs %}
{{ dir }}:
  file.directory:
    - makedirs: true
    - user: hdfs
    - mode: 700
{% endfor %}

start-hadoop-hdfs-datanode:
  service.running:
    - name: hadoop-hdfs-datanode
    - enable: true
    - watch:
      - sls: cdh5.hdfs.conf
      - pkg: hadoop-hdfs-datanode
      {% for dir in datanode_dirs %}
      - file: {{ dir }}
      {% endfor %}
