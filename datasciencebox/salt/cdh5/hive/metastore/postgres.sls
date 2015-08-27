{% from "postgres/settings.sls" import jdbc_jar_path with context %}
{% from "cdh5/hive/settings.sls" import schema_path, postgres_jdbc_symlink_target with context %}

{%- set run_once = '/etc/hive/conf/run_once.touch' %}

include:
  - postgres
  - postgres.jdbc
  - cdh5.hive

create-hive-db-user:
  cmd.run:
    - name: psql -c "CREATE USER hiveuser WITH PASSWORD '';"
    - user: postgres
    - unless: psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='hiveuser'" | grep -q 1
    - require:
      - sls: postgres

create-hive-metastore-db:
  cmd.run:
    - name: psql -c "CREATE DATABASE metastore;"
    - user: postgres
    - unless: psql -l | grep metastore
    - require:
      - sls: postgres

hiveuser-permission:
  cmd.run:
    - name: psql -c "GRANT ALL PRIVILEGES ON DATABASE metastore TO hiveuser;"
    - user: postgres
    - require:
      - cmd: create-hive-db-user
      - cmd: create-hive-metastore-db

hive-table:
  cmd.run:
    - name: psql -U hiveuser -d metastore < {{ schema_path }} && touch {{ run_once }}
    - creates: {{ run_once }}
    - env:
      - PGPASSWORD: "''"
    - require:
      - sls: postgres
      - cmd: create-hive-metastore-db

link-hive-postgres-jdbc:
  file.symlink:
    - name: {{ postgres_jdbc_symlink_target }}
    - target: {{ jdbc_jar_path }}
    - require:
      - sls: postgres
      - sls: postgres.jdbc
      - sls: cdh5.hive
