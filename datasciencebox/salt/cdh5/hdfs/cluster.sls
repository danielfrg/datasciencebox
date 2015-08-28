{% set is_namenode = 'hdfs.namenode' in grains['roles'] %}
{% set is_datanode = 'hdfs.datanode' in grains['roles'] %}

{% if is_namenode or is_datanode %}
include:
  {% if is_namenode %}
  - cdh5.hdfs.namenode
  - cdh5.hdfs.users
  {% endif %}

  {% if is_datanode %}
  - cdh5.hdfs.datanode
  {% endif %}
{% endif %}
