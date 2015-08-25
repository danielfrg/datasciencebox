{%- from 'java/settings.sls' import java with context -%}
{%- from 'system/settings.sls' import user with context -%}
{%- from 'mesos/settings.sls' import mesos with context -%}
{%- from 'spark/settings.sls' import version with context -%}
{%- from 'cdh5/zookeeper/settings.sls' import zk with context -%}
{%- from 'cdh5/hdfs/settings.sls' import namenode_fqdn with context -%}

{% set env = {} %}

{% do env.update({'JAVA_HOME': java.java_home }) %}
{% do env.update({'SPARK_HOME': '/usr/lib/spark' }) %}

{% do env.update({'MESOS_NATIVE_LIBRARY': '/usr/local/lib/libmesos.so' }) %}

{% do env.update({'SPARK_EXECUTOR_URI': 'hdfs://' ~ namenode_fqdn ~ ':8020/spark/' ~ version ~ '.tgz' }) %}
{% do env.update({'MASTER': 'zk://' ~ zk['connection_string'] ~ '/mesos' }) %}
{% do env.update({'CLUSTER_URL': 'mesos://' ~ mesos['master'] ~ ':5050' }) %}

{% do env.update({'PYTHONPATH': '/usr/lib/spark/python:/usr/lib/spark/python/lib/py4j-0.8.2.1-src.zip:$PYTHONPATH' }) %}
{% do env.update({'PYSPARK_SUBMIT_ARGS': '--master mesos://' ~ mesos['master'] ~ ':5050' ~ ' pyspark-shell' }) %}
{% do env.update({'PYSPARK_PYTHON': '/home/{{ user }}/anaconda/bin/python' }) %}
