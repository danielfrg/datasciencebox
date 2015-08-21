include:
  - java

/tmp/spark.tgz:
  file.managed:
    - source: http://d3kbcqa49mib13.cloudfront.net/spark-1.4.1-bin-hadoop2.6.tgz
    - source_hash: md5=858ab5dd5dc0ad4564affbb8a777ad47
    - unless: test -e /usr/lib/spark-1.4.1-bin-hadoop2.6.tgz

untar-spark:
  cmd.run:
    - name: tar -zxf /tmp/spark.tgz -C /usr/lib
    - cwd: /tmp
    - unless: test -e /usr/lib/spark-1.4.1-bin-hadoop2.6.tgz
    - require:
      - file: /tmp/spark.tgz

link-spark:
  cmd.run:
    - name: ln -s /usr/lib/spark-1.4.1-bin-hadoop2.6.tgz /usr/lib/spark
    - unless: test -e /usr/lib/spark
    - require:
      - cmd: untar-spark
