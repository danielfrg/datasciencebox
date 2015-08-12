{%- set force_mine_update = salt['mine.send']('network.ip_addrs') %}
{%- set zookeepers = salt['mine.get']('roles:zookeeper', 'network.ip_addrs', 'grain') %}

{%- set zk_ids = {} %}
{%- set zk_dict_ips = {} %}
{%- set zk_ips = {} %}
{%- for minion_id, ip_addrs in zookeepers.iteritems() %}
{%- do zk_ids.update({minion_id: loop.index0}) %}
{%- do zk_ips.update({minion_id: ip_addrs[0]}) %}
{%- do zk_dict_ips.update({loop.index0: ip_addrs[0]}) %}
{%- endfor %}

{%- set myid = zk_ids.get(grains.id, '') %}

{%- set zkport = '2181' %}
{%- set connection_string = [] %}

{%- for ip_addrs in zk_ips.values() | sort() %}
{%- do connection_string.append(ip_addrs + ':' + zkport) %}
{%- endfor %}

{%- set zk = {} %}
{%- do zk.update({  'myid': myid,
                    'port': zkport,
                    'data_dir': '/var/lib/zookeeper/data',
                    'snap_retain_count': 3,
                    'zookeepers': zk_dict_ips,
                    'connection_string': ','.join(connection_string),
                  })
%}
