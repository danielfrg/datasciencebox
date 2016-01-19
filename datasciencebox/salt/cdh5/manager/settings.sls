{% set force_mine_update = salt['mine.send']('network.get_hostname') %}
{% set metastore_instances = salt['mine.get']('roles:cloudera.manager.server', 'network.get_hostname', 'grain') %}
{% set manager_host = metastore_instances.values()[0] %}
