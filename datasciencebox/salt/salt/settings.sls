{% set is_master = 'salt.master' in grains['roles'] %}
{% set is_minion = 'salt.minion' in grains['roles'] %}


{% set localvars = {} %}

{% if is_master %}
  {% do localvars.update({'my_roles': salt['pillar.get']('salt:minion:head:roles', []) }) %}
{% elif is_minion %}
  {% do localvars.update({'my_roles': salt['pillar.get']('salt:minion:compute:roles', []) }) %}
{% endif %}

{% set my_roles = localvars['my_roles'] %}
