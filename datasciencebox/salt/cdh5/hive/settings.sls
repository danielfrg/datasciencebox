{% set force_mine_update = salt['mine.send']('network.get_hostname') %}
{% set metastore_instances = salt['mine.get']('roles:hive.metastore', 'network.get_hostname', 'grain') %}
{% set metastore_host = metastore_instances.values()[0] %}

{% set schema_path = '/usr/lib/hive/scripts/metastore/upgrade/postgres/hive-schema-1.1.0.postgres.sql' %}
{% set postgres_jdbc_symlink_target = '/usr/lib/hive/lib/postgresql-jdbc4.jar' %}
