{%- from 'spark/settings.sls' import version, source_url with context %}

include:
  - java

## TODO: download and use alternatives to set the version

download-spark:
  cmd.run:
    - name: |
        wget {{ source_url }} -O /tmp/{{ version }}.tgz -q;
        tar -xf /tmp/{{ version }}.tgz && mv {{ version }} spark;
    - cwd: /usr/lib
    - unless: test -e /usr/lib/spark
    - require:
      - sls: java
