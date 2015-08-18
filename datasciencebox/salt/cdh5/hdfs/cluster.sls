{% from "cdh5/hdfs/settings.sls" import is_namenode, is_datanode with context %}

{% if is_namenode or is_datanode %}
include:
  {% if is_namenode %}
  - cdh5.hdfs.namenode
  {% endif %}

  {% if is_datanode %}
  - cdh5.hdfs.datanode
  {% endif %}
{% endif %}
