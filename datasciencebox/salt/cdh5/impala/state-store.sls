include:
  - cdh5.impala

impala-state-store:
  pkg.installed:
    - require:
      - sls: cdh5.impala

start-impala-state-store:
  service.running:
    - name: impala-state-store
    - enable: true
    - watch:
      - sls: cdh5.impala
      - pkg: impala-state-store

hdfs-impala-create:
  cmd.run:
    - name: hadoop fs -mkdir -p /user/impala
    - user: hdfs
    - require:
      - sls: cdh5.impala.conf

hdfs-impala-owner:
  cmd.run:
    - name: hadoop fs -chown impala /user/impala
    - user: hdfs
    - require:
      - cmd: hdfs-impala-create
