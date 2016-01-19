include:
  - cdh5.manager

cloudera-manager-daemons:
  pkg.installed:
    - requires:
      - cdh5.manager

cloudera-manager-server:
  pkg.installed:
    - requires:
      - cdh5.manager

cloudera-manager-server-db-2:
  pkg.installed:
    - requires:
      - cdh5.manager

cloudera-scm-server-db:
  service.running:
    - require:
      - pkg: cloudera-manager-server-db-2

cloudera-scm-server:
  service.running:
    - require:
      - pkg: cloudera-manager-server
      - pkg: cloudera-manager-daemons
      - service: cloudera-scm-server-db
