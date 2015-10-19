{%- from 'cdh5/kudu/settings.sls' import master_ips with context %}

/tmp/kudu.debug:
  file.managed:
    - contents: |
        master_ips: {{ master_ips }}
