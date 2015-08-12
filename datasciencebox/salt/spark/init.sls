include:
  - java

download-spark:
  cmd.run:
    - name: wget http://d3kbcqa49mib13.cloudfront.net/spark-1.3.0-bin-hadoop2.4.tgz -q
    - cwd: /tmp
    - unless: test -e /usr/lib/spark-1.3.0-bin-hadoop2.4

untar-spark:
  cmd.run:
    - name: tar -zxf /tmp/spark-1.3.0-bin-hadoop2.4.tgz -C /usr/lib
    - cwd: /tmp
    - unless: test -e /usr/lib/spark-1.3.0-bin-hadoop2.4

link-spark:
  cmd.run:
    - name: ln -s /usr/lib/spark-1.3.0-bin-hadoop2.4 /usr/lib/spark
    - cwd: /tmp
    - unless: test -e /usr/lib/spark
