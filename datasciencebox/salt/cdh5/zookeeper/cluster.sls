{%- from 'cdh5/zookeeper/settings.sls' import is_server with context %}

{% if is_server %}
include:
  - cdh5.zookeeper.server
{% endif %}
