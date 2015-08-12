include:
  - cdh5.hdfs.namenode

{% for name, user in pillar.get('users', {}).items() if user.absent is not defined or not user.absent %}
{{ name }}-create:
  cmd.run:
    - name: hadoop fs -mkdir -p /user/{{ name }}
    - user: hdfs
    - unless: hadoop fs -test -e /user/{{ name }}

{{ name }}-permision:
  cmd.run:
    - name: hadoop fs -chown {{ name }} /user/{{ name }}
    - user: hdfs
    - require:
      - cmd: {{ name }}-create
{% endfor %}
