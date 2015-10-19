include:
  - cdh5.kudu.repo

master-pkg:
  pkg.installed:
    - name: kudu-master
    - skip_verify: true
    - require:
      - sls: cdh5.kudu.repo

master-conf:
  file.managed:
    - name: /etc/kudu/conf/master.gflagfile
    - source: salt://cdh5/etc/kudu/master.gflagfile
    - template: jinja
    - require:
      - pkg: master-pkg

master-start:
  service.running:
    - name: kudu-master
    - enable: true
    - watch:
      - file: master-conf
