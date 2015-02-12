include:
  - java
  - cdh5

zookeeper-pkg:
  pkg.installed:
    - name: zookeeper-server
    - require:
      - sls: cdh5

zookeeper:
  cmd.run:
    - name: service zookeeper-server init
    - unless: test -e /var/lib/zookeeper/version-2
  service.running:
    - name: zookeeper-server
    - require:
      - cmd: zookeeper
      - pkg: zookeeper-pkg

# TODO /etc/zookeeper/conf/zoo.cfg
# TODO /var/lib/zookeeper/myid
