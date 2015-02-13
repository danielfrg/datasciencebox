{%- set force_mine_update = salt['mine.send']('network.ip_addrs') %}

{%- set masters_dict = salt['mine.get']('roles:mesos.master', 'network.ip_addrs', 'grain') %}

{%- set masters_ips = {} %}
{%- set masters_ids = {} %}
{%- set zookeepers = {} %}
{%- for minion_id, ip_addrs in masters_dict.iteritems() %}
{%- do masters_ids.update({minion_id: loop.index0}) %}
{%- do masters_ips.update({minion_id: ip_addrs[0]}) %}
{%- do zookeepers.update({loop.index0: ip_addrs[0]}) %}
{%- endfor %}
{%- set num_masters = masters_ips | length() %}

{%- set myid = masters_ids.get(grains.id, '') %}

{%- set zkport = '2181' %}
{%- set connection_string = [] %}
{%- for ip_addrs in masters_ips.values() | sort() %}
{%- do connection_string.append(ip_addrs + ':' + zkport) %}
{%- endfor %}

{%- set zk = {} %}
{%- do zk.update({  'myid': myid,
                    'port': zkport,
                    'data_dir': '/var/zookeeper',
                    'snap_retain_count': 3,
                    'zookeepers': zookeepers,
                  })
%}

{%- set myip = salt['network.ip_addrs']('eth0')[0] %}

{%- set mesos = {} %}
{%- do mesos.update({ 'myip': myip,
                      'dict': masters_dict,
                      'zk': zk,
                      'master': masters_ips.get(grains.id),
                      'connection_string' : ','.join(connection_string),
                  })
%}
