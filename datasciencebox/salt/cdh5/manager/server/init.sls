include:
  - cdh5.manager

server-packages:
  pkg.installed:
    - names:
      - cloudera-manager-daemons
      - cloudera-manager-server-db-2
      - cloudera-manager-server
    - requires:
      - cdh5.manager

server-services:
  service.running:
    - names:
      - cloudera-scm-server-db
      - cloudera-scm-server
    - require:
      - pkg: server-packages
