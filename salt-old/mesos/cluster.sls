include:
  - salt.master
  - salt.cloud

{% set slaves = pillar['mesos']['cluster']['slaves'] %}
/etc/salt/cloud.maps.d/mesos-cluster.map:
  file.managed:
    - contents: |
        mesos-slave:
          {% for instance in range(slaves) %}
          - mesos-slave-{{ instance + 1 }}
          {% endfor %}
    - require:
      - sls: salt.master
      - sls: salt.cloud

create-mesos-cluster:
  cmd.run:
    - name: salt-cloud -m /etc/salt/cloud.maps.d/mesos-cluster.map -P -y
    - require:
      - file: /etc/salt/cloud.maps.d/mesos-cluster.map
