include:
  - cdh5.hive
  - cdh5.hive.metastore.postgres

hive-metastore:
  pkg.installed:
    - require:
      - sls: cdh5.hive

start-hive-metastore:
  service.running:
    - name: hive-metastore
    - enable: True
    - watch:
      - sls: cdh5.hive
      - sls: cdh5.hive.metastore.postgres

hdfs-hive-create:
  cmd.run:
    - name: hadoop fs -mkdir -p /user/hive/warehouse
    - user: hdfs
    - require:
      - sls: cdh5.hive

hdfs-hive-owner:
  cmd.run:
    - name: hadoop fs -chown hive /user/hive/warehouse
    - user: hdfs
    - require:
      - cmd: hdfs-hive-create

hdfs-hive-permissions:
  cmd.run:
    - name: hadoop fs -chmod 1777 /user/hive/warehouse
    - user: hdfs
    - require:
      - cmd: hdfs-hive-create
