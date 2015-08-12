{%- set force_mine_update = salt['mine.send']('network.ip_addrs') %}
{%- set masters_dict = salt['mine.get']('roles:mesos.master', 'network.ip_addrs', 'grain') %}

{%- set masters_ips = [] %}
{%- for minion_id, ip_addrs in masters_dict.iteritems() %}
{%- do masters_ips.append(ip_addrs[0]) %}
{%- endfor %}

{%- set myip = salt['network.ip_addrs']('eth0')[0] %}

{%- set mesos = {} %}
{%- do mesos.update({ 'myip': myip,
                      'master': masters_ips[0],
                  })
%}
