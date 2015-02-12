include:
  - users
  - mesos.conf
  - cdh5.zookeeper

mesos-master:
  service.running:
    - name: mesos-master
    - enable: true
    - require:
      - sls: mesos.conf
      - sls: cdh5.zookeeper

mesos-slave-dead:
  service.dead:
    - name: mesos-slave
    - require:
      - sls: mesos.conf
  cmd.run:
    - name: echo manual > /etc/init/mesos-slave.override
    - require:
      - sls: mesos.conf
