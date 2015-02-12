{%- set force_mine_update = salt['mine.send']('network.get_hostname') %}

{%- set masters = salt['mine.get']('roles:mesos-master', 'network.get_hostname', 'grain') %}
{%- set masters = masters.values() %}
{% if masters | length > 0 %}
{%- set master_fqdn = masters[0] %}
{% else %}
{%- set master_fqdn = 'localhost' %}
{% endif %}
