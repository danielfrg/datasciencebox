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
