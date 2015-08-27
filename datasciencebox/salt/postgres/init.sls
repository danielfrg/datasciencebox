{%- from 'postgres/settings.sls' import pg_hba_conf with context -%}

postgres-install:
  pkg.installed:
    - name: postgresql

pg_hba.conf:
  file.managed:
    - name: {{ pg_hba_conf }}
    - source: salt://postgres/templates/pg_hba.conf
    - template: jinja
    - user: postgres
    - group: postgres
    - mode: 644
    - require:
      - pkg: postgres-install

postgresql:
  service.running:
    - name: postgresql
    - enable: true
    - watch:
      - file: pg_hba.conf
