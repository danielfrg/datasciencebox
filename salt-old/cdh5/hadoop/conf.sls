{%- from 'cdh5/settings.sls' import namenode_fqdn, namenode_dirs, datanode_dirs with context %}

include:
  - hostsfile

/etc/hadoop/conf:
  file.recurse:
    - source: salt://cdh5/etc/hadoop/conf
    - template: jinja
    - user: root
    - group: root
    - file_mode: 644
    - context:
      namenode_fqdn: {{ namenode_fqdn }}
      namenode_dirs: {{ namenode_dirs }}
      datanode_dirs: {{ datanode_dirs }}
    - require:
      - sls: hostsfile
