{%- from 'spark/settings.sls' import version, source_url, source_hash, spark_home with context -%}

include:
  - java

/tmp/{{ version }}.tgz:
  file.managed:
    - source: {{ source_url }}
    - source_hash: {{ source_hash }}
    - unless: test -e /tmp/{{ version }}.tgz

untar-spark:
  cmd.run:
    - name: tar -zxf /tmp/{{ version }}.tgz -C /usr/lib
    - cwd: /tmp
    - unless: test -e /usr/lib/{{ version }}
    - require:
      - file: /tmp/{{ version }}.tgz

link-spark:
  cmd.run:
    - name: ln -s /usr/lib/{{ version }} {{ spark_home }}
    - unless: test -L {{ spark_home }}
    - require:
      - cmd: untar-spark
