{%- from 'cdh5/zookeeper/settings.sls' import zk with context %}

include:
  - cdh5

zookeeper-pkg:
  pkg.installed:
    - name: zookeeper-server

zookeeper-server-init-stop:
  cmd.run:
    - name: service zookeeper-server stop
    - unless: test -e {{ zk['data_dir'] }}/version-2

{{ zk['data_dir'] }}:
  file.directory:
    - user: zookeeper

zookeeper-server-init:
  cmd.wait:
    - name: service zookeeper-server init
    - unless: test -e {{ zk['data_dir'] }}/version-2
    - watch:
      - file: {{ zk['data_dir'] }}
      - cmd: zookeeper-server-init-stop

{{ zk['data_dir'] }}/myid:
  file.managed:
    - source: salt://cdh5/etc/zookeeper/conf/myid
    - template: jinja
    - makedirs: true
    - context:
      id: {{ zk['myid'] }}
    - require:
      - file: {{ zk['data_dir'] }}
      - cmd: zookeeper-server-init

/etc/zookeeper/conf/zoo.cfg:
  file.managed:
    - source: salt://cdh5/etc/zookeeper/conf/zoo.cfg
    - template: jinja
    - makedirs: true
    - context:
      port: {{ zk['port'] }}
      data_dir: {{ zk['data_dir'] }}
      snap_retain_count: {{ zk['snap_retain_count'] }}
      zookeepers: {{ zk['zookeepers'] }}
    - require:
      - cmd: zookeeper-server-init

zookeeper-server:
  service.running:
    - name: zookeeper-server
    - enable: true
    - watch:
      - cmd: zookeeper-server-init
      - file: {{ zk['data_dir'] }}/myid
      - file: /etc/zookeeper/conf/zoo.cfg
