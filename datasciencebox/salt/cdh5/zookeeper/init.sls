{%- from 'cdh5/zookeeper/settings.sls' import zk with context %}

include:
  - java
  - cdh5.repo

zookeeper-pkg:
  pkg.installed:
    - name: zookeeper-server

data_dir:
  file.directory:
    - name: {{ zk['data_dir'] }}
    - user: zookeeper

/etc/zookeeper/conf/zoo.cfg:
  file.managed:
    - source: salt://cdh5/etc/zookeeper/conf/zoo.cfg
    - template: jinja
    - makedirs: true
    - require:
      - pkg: zookeeper-pkg

zookeeper-server-init:
  cmd.run:
    - name: service zookeeper-server stop && service zookeeper-server init
    - unless: test -e {{ zk['data_dir'] }}/version-2
    - require:
      - file: data_dir
      - file: /etc/zookeeper/conf/zoo.cfg

zk-myid:
  file.managed:
    - name: {{ zk['data_dir'] }}/myid
    - source: salt://cdh5/etc/zookeeper/conf/myid
    - template: jinja
    - makedirs: true
    - require:
      - pkg: zookeeper-pkg
      - cmd: zookeeper-server-init
