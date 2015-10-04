{% from "salt/settings.sls" import is_master, is_minion with context %}

{% if is_master or is_minion %}
include:
  {% if is_master %}
  - salt.master
  {% endif %}

  {% if is_minion %}
  - salt.minion
  {% endif %}
{% endif %}
