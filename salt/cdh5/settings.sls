{%- set force_mine_update = salt['mine.send']('network.get_hostname') %}

{%- set namenodes = salt['mine.get']('roles:namenode', 'network.get_hostname', 'grain') %}
{%- set namenodes = namenodes.values() %}
{% if namenodes | length > 0 %}
{%- set namenode_fqdn = namenodes[0] %}
{% else %}
{%- set namenode_fqdn = 'localhost' %}
{% endif %}

# Namenode and Datanode directories
{%- set namenode_dirs = []  %}
{%- set datanode_dirs = [] %}
{% set mounted = salt['mount.fstab']() %}

{% if mounted | length == 1 %}
{% do namenode_dirs.append('/data/dfs/nn') %}
{% do datanode_dirs.append('/data/dfs/dn') %}
{% else %}
{% for disk in mounted.keys() %}
  {% if disk != '/' %}
    {% do namenode_dirs.append((disk ~ '/data/dfs/nn').encode('utf8')) %}
    {% do datanode_dirs.append((disk ~ '/data/dfs/dn').encode('utf8')) %}
  {% endif %}
{% endfor %}
{% endif %}
