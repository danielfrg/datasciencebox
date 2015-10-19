{% from "system/settings.sls" import is_vagrant with context %}

{% set localvars = {} %}

{% if is_vagrant %}
  {% do localvars.update({'interface': 1}) %}
{% else %}
  {% do localvars.update({'interface': 0}) %}
{% endif %}

{% set is_master = 'kudu.master' in grains['roles'] %}
{% set is_tserver = 'kudu.tserver' in grains['roles'] %}

{% set force_mine_update = salt['mine.send']('network.ip_addrs') %}
{% set master_instances = salt['mine.get']('roles:kudu.master', 'network.ip_addrs', 'grain') %}

{% set master_ips = [] %}
{% for minion_id, ip_addrs in master_instances.iteritems() %}
  {% do master_ips.append(ip_addrs[localvars['interface']]) %}
{% endfor %}
