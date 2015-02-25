{%- from 'mesos/settings.sls' import mesos with context %}

include:
  - mesos.conf

/etc/mesos-master/ip:
  file.managed:
    - source: salt://mesos/etc/mesos/ip
    - template: jinja
    - makedirs: true
    - context:
      ip: {{ mesos['myip'] }}
    - makedirs: true

/etc/mesos-master/hostname:
  file.managed:
    - source: salt://mesos/etc/mesos/ip
    - template: jinja
    - makedirs: true
    - context:
      ip: {{ mesos['myip'] }}
    - makedirs: true

mesos-master:
  service.running:
    - name: mesos-master
    - enable: true
    - watch:
      - sls: mesos.conf
      - file: /etc/mesos-master/ip
      - file: /etc/mesos-master/hostname

mesos-slave-dead:
  service.dead:
    - name: mesos-slave
    - require:
      - sls: mesos.conf
  cmd.run:
    - name: echo manual > /etc/init/mesos-slave.override
    - unless: test -e /etc/init/mesos-slave.override
    - require:
      - sls: mesos.conf

# zookeeper-dead:
#   cmd.run:
#     - name: echo manual > /etc/init/zookeeper.override
#     - unless: test -e /etc/init/zookeeper.override
#     - require:
#       - sls: mesos.conf
#   service.dead:
#     - name: zookeeper
#     - require:
#       - cmd: zookeeper-dead
