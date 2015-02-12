include:
  - users
  - mesos.conf

mesos-slave:
  service.running:
    - name: mesos-slave
    - enable: true
    - require:
      - sls: mesos.conf

mesos-master-dead:
  service.dead:
    - name: mesos-master
    - require:
      - sls: mesos.conf
  cmd.run:
    - name: echo manual > /etc/init/mesos-slave.override
    - require:
      - sls: mesos.conf

zookeeper-dead:
  service.dead:
    - name: zookeeper
    - require:
      - sls: mesos.conf
  cmd.run:
    - name: echo manual > /etc/init/zookeeper.override
    - require:
      - sls: mesos.conf
