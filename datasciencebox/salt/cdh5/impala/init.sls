include:
  - cdh5.repo

impala:
  pkg.installed:
    - require:
      - sls: cdh5

/etc/default/impala:
  file.managed:
    - source: salt://cdh5/etc/default/impala
    - template: jinja
    - user: root
    - group: root
    - makedirs: true

/etc/impala/conf/core-site.xml:
  file.managed:
    - source: salt://cdh5/etc/impala/conf/core-site.xml
    - template: jinja
    - user: root
    - group: root
    - require:
      - pkg: impala

/etc/impala/conf/hdfs-site.xml:
  file.managed:
    - source: salt://cdh5/etc/impala/conf/hdfs-site.xml
    - template: jinja
    - user: root
    - group: root
    - require:
      - pkg: impala

/etc/impala/conf/hive-site.xml:
  file.managed:
    - source: salt://cdh5/etc/impala/conf/hive-site.xml
    - template: jinja
    - user: root
    - group: root
    - require:
      - pkg: impala
