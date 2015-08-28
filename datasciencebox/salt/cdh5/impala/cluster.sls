{% set is_state_store = 'impala.state-store' in grains['roles'] %}
{% set is_server = 'impala.server' in grains['roles'] %}

{% if is_state_store or is_server %}
include:
  {% if is_state_store %}
  - cdh5.impala.state-store
  - cdh5.impala.catalog
  {% endif %}

  {% if is_server %}
  - cdh5.impala.server
  {% endif %}
{% endif %}
