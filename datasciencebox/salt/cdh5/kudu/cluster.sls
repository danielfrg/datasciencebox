{% from "cdh5/kudu/settings.sls" import is_master, is_tserver with context %}

{% if is_master or is_tserver %}
include:
  {% if is_master %}
  - cdh5.kudu.master
  {% endif %}

  {% if is_tserver %}
  - cdh5.kudu.tserver
  {% endif %}
{% endif %}
