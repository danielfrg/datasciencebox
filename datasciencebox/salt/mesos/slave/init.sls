{%- from 'mesos/settings.sls' import mesos with context %}

include:
  - mesos.conf

/etc/mesos-slave/ip:
  file.managed:
    - source: salt://mesos/etc/mesos/ip
    - template: jinja
    - makedirs: true
    - context:
      ip: {{ mesos['myip'] }}
    - makedirs: true

/etc/mesos-slave/hostname:
  file.managed:
    - source: salt://mesos/etc/mesos/ip
    - template: jinja
    - makedirs: true
    - context:
      ip: {{ mesos['myip'] }}
    - makedirs: true

# /etc/mesos-slave/containerizers:
#   file.managed:
#     - source: salt://mesos/etc/mesos/ip
#     - template: jinja
#     - makedirs: true
#     - context:
#       ip: docker,mesos
#     - makedirs: true

/etc/mesos-slave/executor_registration_timeout:
  file.managed:
    - source: salt://mesos/etc/mesos/ip
    - template: jinja
    - makedirs: true
    - context:
      ip: 5mins
    - makedirs: true

mesos-slave:
  service.running:
    - name: mesos-slave
    - enable: true
    - watch:
      - sls: mesos.conf
      - file: /etc/mesos-slave/ip
      - file: /etc/mesos-slave/hostname
      - file: /etc/mesos-slave/executor_registration_timeout

mesos-master-dead:
  cmd.run:
    - name: echo manual > /etc/init/mesos-master.override
    - unless: test -e /etc/init/mesos-master.override
    - require:
      - sls: mesos.conf
  service.dead:
    - name: mesos-master
    - require:
      - cmd: mesos-master-dead

zookeeper-dead:
  cmd.run:
    - name: echo manual > /etc/init/zookeeper.override
    - unless: test -e /etc/init/zookeeper.override
    - require:
      - sls: mesos.conf
  service.dead:
    - name: zookeeper
    - require:
      - cmd: zookeeper-dead
