cdh5-apt:
  file.managed:
    - name: /etc/apt/sources.list.d/cloudera.list
    - source: salt://cdh5/etc/apt/sources.list.d/cloudera.list
    - template: jinja

cdh5-apt-key:
  cmd.run:
    - name: curl -s https://archive.cloudera.com/cdh5/ubuntu/{{ grains["oscodename"] }}/amd64/cdh/archive.key | sudo apt-key add -
    - unless: apt-key list | grep "Cloudera Apt Repository"

cm5-apt:
  file.managed:
    - name: /etc/apt/sources.list.d/cloudera.list
    - source: salt://cdh5/etc/apt/sources.list.d/cloudera.list
    - template: jinja

cm5-apt-key:
  cmd.run:
    - name: curl -s https://archive.cloudera.com/cm5/ubuntu/{{ grains["oscodename"] }}/amd64/cdh/archive.key | sudo apt-key add -
    - unless: apt-key list | grep "Cloudera Apt Repository"

cdh5_refresh_db:
  module.wait:
    - name: pkg.refresh_db
    - watch:
      - file: cm5-apt
      - file: cdh5-apt
      - cmd: cm5-apt-key
      - cmd: cdh5-apt-key

{% if grains["oscodename"] == 'trusty' %}
cloudera-pref:
  file.managed:
    - name: /etc/apt/preferences.d/cloudera.pref
    - source: salt://cdh5/etc/apt/preferences.d/cloudera.pref
    - template: jinja
{% endif %}
