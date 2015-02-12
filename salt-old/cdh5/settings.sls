{%- set force_mine_update = salt['mine.send']('network.get_hostname') %}

{%- set namenodes = salt['mine.get']('roles:namenode', 'network.get_hostname', 'grain') %}
{%- set namenodes = namenodes.values() %}
{% if namenodes | length > 0 %}
{%- set namenode_fqdn = namenodes[0] %}
{% else %}
{%- set namenode_fqdn = 'localhost' %}
{% endif %}

{%- set namenode_dirs = ['/data/1/dfs/nn'] %}
{%- set datanode_dirs = ['/data/1/dfs/dn', '/data/2/dfs/dn'] %}
