{%- from 'mesos/settings.sls' import mesos with context %}

include:
  - mesos

/etc/mesos/zk:
  file.managed:
    - source: salt://mesos/etc/mesos/zk
    - template: jinja
    - makedirs: true
    - context:
      connection_string: {{ mesos['connection_string'] }}
