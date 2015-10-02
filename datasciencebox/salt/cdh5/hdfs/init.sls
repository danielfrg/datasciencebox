/etc/hadoop/conf:
  file.recurse:
    - source: salt://cdh5/etc/hadoop/conf
    - template: jinja
    - user: root
    - group: root
    - file_mode: 644
