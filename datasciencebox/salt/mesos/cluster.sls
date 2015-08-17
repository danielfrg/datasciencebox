{% from "mesos/settings.sls" import is_master, is_slave with context %}

{% if is_master or is_slave %}
include:
  {% if is_master %}
  - mesos.master
  {% endif %}

  {% if is_slave %}
  - mesos.slave
  {% endif %}
{% endif %}
