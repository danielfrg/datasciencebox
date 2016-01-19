{% set is_server = 'cloudera.manager.server' in grains['roles'] %}
{% set is_agent = 'cloudera.manager.agent' in grains['roles'] %}

{% if is_server or is_agent %}
include:
  {% if is_server %}
  - cdh5.manager.server
  - cdh5.manager.agent
  {% endif %}

  {% if is_agent %}
  - cdh5.manager.agent
  {% endif %}
{% endif %}
