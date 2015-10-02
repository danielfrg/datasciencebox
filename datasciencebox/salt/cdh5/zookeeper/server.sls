{%- from 'cdh5/zookeeper/settings.sls' import zk with context %}

include:
  - java
  - cdh5.zookeeper

zookeeper-server:
  service.running:
    - name: zookeeper-server
    - enable: true
    - watch:
      - sls: cdh5.zookeeper
