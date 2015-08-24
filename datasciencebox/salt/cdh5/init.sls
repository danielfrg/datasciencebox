include:
  - java

cdh5-repository_1.0_all.deb:
  file.managed:
    - name: /tmp/cdh5-repository_1.0_all.deb
    - source: http://archive.cloudera.com/cdh5/one-click-install/{{ grains["lsb_distrib_codename"] }}/amd64/cdh5-repository_1.0_all.deb
    - source_hash: md5=9b389af68827bfd704739796e7044961
    - unless: 'apt-key list | grep "Cloudera Apt Repository"'

cdh5_gpg:
  cmd.run:
    - name: dpkg -i /tmp/cdh5-repository_1.0_all.deb
    - unless: 'apt-key list | grep "Cloudera Apt Repository"'
    - require:
      - file: cdh5-repository_1.0_all.deb

cdh5_refresh_db:
  module.wait:
    - name: pkg.refresh_db
    - watch:
      - cmd: cdh5_gpg

{% if grains["oscodename"] == 'trusty' %}
cloudera-pref:
  file.managed:
    - name: /etc/apt/preferences.d/cloudera.pref
    - source: salt://cdh5//etc/apt/preferences.d/cloudera.pref
    - template: jinja
{% endif %}
