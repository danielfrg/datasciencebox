{% from "system/settings.sls" import is_vagrant with context %}

{% set localvars = {} %}

{% if is_vagrant %}
  {% do localvars.update({'interface': 'eth1'}) %}
{% else %}
  {% do localvars.update({'interface': 'eth0'}) %}
{% endif %}

{% set is_master = 'mesos.master' in grains['roles'] %}
{% set is_slave = 'mesos.slave' in grains['roles'] %}

{%- set force_mine_update = salt['mine.send']('network.ip_addrs') %}
{%- set masters_dict = salt['mine.get']('roles:mesos.master', 'network.ip_addrs', 'grain') %}

{%- set masters_ips = [] %}
{%- for minion_id, ip_addrs in masters_dict.iteritems() %}
{%- do masters_ips.append(ip_addrs[0]) %}
{%- endfor %}

{%- set myip = salt['network.ip_addrs'](localvars['interface'])[0] %}

{%- set mesos = {} %}
{%- do mesos.update({ 'myip': myip,
                      'master': masters_ips[0],
                      'is_master': is_master,
                      'is_slave': is_slave,
                    })
%}
