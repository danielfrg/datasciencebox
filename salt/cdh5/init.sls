include:
  - java

cdh5-repository_1.0_all.deb:
  file.managed:
    - name: /tmp/cdh5-repository_1.0_all.deb
    - source: http://archive.cloudera.com/cdh5/one-click-install/{{ grains["lsb_distrib_codename"] }}/amd64/cdh5-repository_1.0_all.deb
    - source_hash: md5=edca32f41320cedde7884e5cb981a3b6
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

# # This is used on ubuntu so that services don't start
# add_policy_file:
#   file.managed:
#     - name: /usr/sbin/policy-rc.d
#     - contents: exit 101
#     - makedirs: true
#     - unless: test -e /usr/sbin/policy-rc.d

# remove_policy_file:
#   file.absent:
#     - name: /usr/sbin/policy-rc.d
#     - require:
#       - file: add_policy_file
