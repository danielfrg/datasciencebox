{% from "salt/package-map.jinja" import pkgs with context %}
{% from "salt/settings.sls" import my_roles with context %}

include:
  - salt.pkgrepo

{% if my_roles is defined %}
/etc/salt/grains:
  file.managed:
    - source: salt://salt/templates/grains
    - template: jinja
    - makedirs: true
    - context:
      roles: {{ my_roles }}
{% endif %}

salt-minion:
  pkg.installed:
    - name: {{ pkgs['salt-minion'] }}
    - skip_verify: true
  file.managed:
    - name: /etc/salt/minion
    - template: jinja
    - source: salt://salt/templates/minion
    - require:
      - pkg: salt-minion
  service.running:
    - enable: true
    - restart: true
    - watch:
      - pkg: salt-minion
      - file: salt-minion
      {% if pillar['salt']['minion']['roles'] is defined %}
      - file: /etc/salt/grains
      {% endif %}
