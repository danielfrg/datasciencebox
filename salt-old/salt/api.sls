{% from "salt/package-map.jinja" import pkgs with context %}

python-pip:
  pkg.installed

# ubuntu 14.04
# CherryPy:
#   cmd.run:
#     - name: pip install CherryPy --no-use-wheel
#     - require:
#       - pkg: python-pip

# ubuntu 13.10
CherryPy:
  pip.installed:
    - require:
      - pkg: python-pip

salt-api:
  pkg.installed:
    - name: {{ pkgs['salt-api'] }}
    - require:
      - pip: CherryPy
  service.running:
    - enable: True
    - watch:
      - pkg: salt-api
