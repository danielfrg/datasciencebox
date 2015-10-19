include:
  - cdh5.kudu.repo

tserver-pkg:
  pkg.installed:
    - name: kudu-tserver
    - skip_verify: true
    - require:
      - sls: cdh5.kudu.repo

tserver-conf:
  file.managed:
    - name: /etc/kudu/conf/tserver.gflagfile
    - source: salt://cdh5/etc/kudu/tserver.gflagfile
    - template: jinja
    - require:
      - pkg: tserver-pkg

tserver-start:
  service.running:
    - name: kudu-tserver
    - enable: true
    - watch:
      - file: tserver-conf
