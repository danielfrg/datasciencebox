include:
  - users
  - s3cmd

s3cmd-config:
  file.managed:
    - name: /home/dsb/.s3cfg
    - source: salt://s3cmd/files/s3cfg.template
    - template: jinja
    - user: dsb
    - mode: 0600
    - require:
      - sls: users
