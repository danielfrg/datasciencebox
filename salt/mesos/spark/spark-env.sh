{%- from 'mesos/spark/settings.sls' import env with context -%}

{% for var in env %}
export {{ var }}="{{ env[var] }}"
{% endfor %}
