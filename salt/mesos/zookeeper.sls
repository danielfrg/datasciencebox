{%- from 'mesos/settings.sls' import mesos with context %}

include:
  - mesos
  - mesos.conf

{{ mesos['zk']['data_dir'] }}:
  file.directory:
    - user: zookeeper

{{ mesos['zk']['data_dir'] }}/myid:
  file.managed:
    - source: salt://mesos/etc/zookeeper/conf/myid
    - template: jinja
    - makedirs: true
    - context:
      id: {{ mesos['zk']['myid'] }}
    - require:
      - file: {{ mesos['zk']['data_dir'] }}

/etc/zookeeper/conf/zoo.cfg:
  file.managed:
    - source: salt://mesos/etc/zookeeper/conf/zoo.cfg
    - template: jinja
    - makedirs: true
    - context:
      port: {{ mesos['zk']['port'] }}
      data_dir: {{ mesos['zk']['data_dir'] }}
      snap_retain_count: {{ mesos['zk']['snap_retain_count'] }}
      zookeepers: {{ mesos['zk']['zookeepers'] }}
    - require:
      - file: {{ mesos['zk']['data_dir'] }}/myid

zookeeper:
  service.running:
    - name: zookeeper
    - enable: true
    - restart: true
    - watch:
      - file: {{ mesos['zk']['data_dir'] }}/myid
      - file: /etc/zookeeper/conf/zoo.cfg
