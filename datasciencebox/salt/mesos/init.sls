include:
  - mesos.repo

mesos:
  pkg.installed:
    - name: mesos
    - require:
      - sls: mesos.repo
