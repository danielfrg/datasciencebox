{% from "salt/package-map.jinja" import pkgs with context %}

include:
  - salt.pkgrepo

salt-minion:
  pkg.installed:
    - name: {{ pkgs['salt-minion'] }}
  file.managed:
    - name: /etc/salt/minion
    - template: jinja
    - source: salt://salt/templates/minion
  service.running:
    - enable: true
    - restart: true
    - watch:
      - pkg: salt-minion
      - file: salt-minion
