include:
  - cdh5.impala

impala-server:
  pkg.installed:
    - require:
      - sls: cdh5.impala

impala-shell:
  pkg.installed:
    - require:
      - sls: cdh5.impala

setup-hdfs-sockets:
  file.directory:
    - name: /var/run/hadoop-hdfs/dn
    - makedirs: true
    - group: root
    - require:
        - pkg: impala-server

start-impala-server:
  service.running:
    - name: impala-server
    - enable: true
    - watch:
      - sls: cdh5.impala
      - pkg: impala-shell
      - pkg: impala-server
