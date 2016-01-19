include:
  - cdh5.manager

agent-packages:
  pkg.installed:
    - names:
      - cloudera-manager-daemons
      - cloudera-manager-agent
    - requires:
      - cdh5.manager

/etc/cloudera-scm-agent/config.ini:
  file.managed:
    - source: salt://cdh5/etc/cloudera-scm-agent/config.ini
    - template: jinja

agent-services:
  service.running:
    - names:
      - cloudera-scm-agent
    - require:
      - pkg: agent-packages
