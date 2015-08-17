{%- from 'mesos/settings.sls' import mesos with context %}

include:
  - mesos

marathon-pkg:
  pkg.installed:
    - name: marathon
    - require:
      - sls: mesos

marathon-service:
  service.running:
    - name: marathon
    - enable: true
    - watch:
      - pkg: marathon-pkg
