{%- from 'cdh5/zookeeper/settings.sls' import zk with context %}

include:
  - mesos

/etc/mesos/zk:
  file.managed:
    - source: salt://mesos/etc/mesos/zk
    - template: jinja
    - makedirs: true
    - context:
      connection_string: {{ zk['connection_string'] }}
