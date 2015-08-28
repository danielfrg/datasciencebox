{%- from 'system/settings.sls' import user with context %}
{%- set users = [user] -%}

include:
  - cdh5.hdfs.namenode

{% for name in users %}
{{ name }}-create:
  cmd.run:
    - name: hadoop fs -mkdir -p /user/{{ name }}
    - user: hdfs
    - unless: hadoop fs -test -e /user/{{ name }}
    - require:
      - sls: cdh5.hdfs.namenode

{{ name }}-permision:
  cmd.run:
    - name: hadoop fs -chown {{ name }} /user/{{ name }}
    - user: hdfs
    - require:
      - cmd: {{ name }}-create

{{ name }}-hadoop-group:
  user.present:
    - name: {{ user }}
    - remove_groups: false
    - groups:
      - hadoop
{% endfor %}
