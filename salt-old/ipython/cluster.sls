include:
  - salt.master
  - salt.cloud

{% set instances = pillar['ipython']['cluster']['instances'] %}
/etc/salt/cloud.maps.d/ipython-cluster.map:
  file.managed:
    - contents: |
        ipython-engine:
          {% for instance in range(instances) %}
          - ipython-engine-{{ instance + 1 }}
          {% endfor %}
    - require:
      - sls: salt.master
      - sls: salt.cloud

create-ipython-cluster:
  cmd.run:
    - name: salt-cloud -m /etc/salt/cloud.maps.d/ipython-cluster.map -P -y
    - require:
      - file: /etc/salt/cloud.maps.d/ipython-cluster.map
