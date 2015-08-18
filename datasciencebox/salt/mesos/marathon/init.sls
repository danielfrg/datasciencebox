{%- from 'mesos/settings.sls' import mesos with context -%}
{%- from 'supervisor/settings.sls' import conf_d with context -%}

include:
  - mesos
  - supervisor

marathon-pkg:
  pkg.installed:
    - name: marathon
    - require:
      - sls: mesos

# For some reason the service is not showing up the UI but supervisor does
marathon-service:
  service.dead:
    - name: marathon
    - enable: true
    - watch:
      - pkg: marathon-pkg

marathon.conf:
  file.managed:
    - name: {{ conf_d }}/marathon.conf
    - source: salt://mesos/marathon/marathon.conf
    - template: jinja
    - makedirs: true

marathon-running:
  supervisord.running:
    - name: marathon
    - update: true
    - restart: false
    - watch:
      - file: marathon.conf
      - pkg: marathon-pkg
