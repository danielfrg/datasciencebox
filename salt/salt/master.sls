{% from "salt/package-map.jinja" import pkgs with context %}

include:
  - salt.pkgrepo

salt-master:
  pkg.installed:
    - name: {{ pkgs['salt-master'] }}
  file.managed:
    - name: /etc/salt/master
    - template: jinja
    - source: salt://salt/templates/master
  service.running:
    - enable: true
    - restart: true
    - watch:
      - pkg: salt-master
      - file: salt-master
