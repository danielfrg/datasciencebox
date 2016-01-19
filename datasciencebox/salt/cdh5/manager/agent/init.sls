include:
  - cdh5.manager

cloudera-manager-daemons:
  pkg.installed:
    - requires:
      - cdh5.manager

cloudera-manager-agent:
  pkg.installed:
    - requires:
      - cdh5.manager

/etc/cloudera-scm-agent/config.ini:
  file.managed:
    - source: salt://cdh5/etc/cloudera-scm-agent/config.ini
    - template: jinja

cloudera-scm-agent:
  service.running:
    - require:
      - pkg: cloudera-manager-agent
