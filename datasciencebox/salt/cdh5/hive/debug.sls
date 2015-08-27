{%- from 'cdh5/hive/settings.sls' import metastore_instances, metastore_host with context %}

/tmp/hive.debug:
  file.managed:
    - contents: |
        metastore_instances: {{ metastore_instances }}
        metastore_host: {{ metastore_host }}
