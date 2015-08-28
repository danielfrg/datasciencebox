include:
  - cdh5.impala

impala-catalog:
  pkg.installed:
    - require:
      - sls: cdh5.impala

start-impala-catalog:
  service.running:
    - name: impala-catalog
    - enable: true
    - watch:
      - sls: cdh5.impala
      - pkg: impala-catalog
