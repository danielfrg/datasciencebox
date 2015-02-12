# Requires cdh5.hadoop.namenode or cdh5.hadoop.datanode

tmp-create:
  cmd.run:
    - name: hadoop fs -mkdir -p /tmp
    - user: hdfs
    - require:
      - sls: cdh5.hadoop.namenode

tmp-permision:
  cmd.run:
    - name: hadoop fs -chmod -R 1777 /tmp
    - user: hdfs
    - require:
      - cmd: tmp-create

{% for name, user in pillar.get('users', {}).items() if user.absent is not defined or not user.absent %}
{{ name }}-create:
  cmd.run:
    - name: hadoop fs -mkdir -p /user/{{ name }}
    - user: hdfs
    - require:
      - sls: cdh5.hadoop.namenode

{{ name }}-permision:
  cmd.run:
    - name: hadoop fs -chown {{ name }} /user/{{ name }}
    - user: hdfs
    - require:
      - cmd: {{ name }}-create
{% endfor %}
