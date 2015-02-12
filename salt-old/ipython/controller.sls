include:
  - python

ipcontroller-pkgs:
  conda.installed:
    - name: pyzmq,ipython
    - env: /home/dsb/envs/base
    - user: dsb
    - require:
      - sls: python

controller-log:
  file.directory:
    - name: /var/log/ipython
    - makedirs: true

ipcontroller.conf:
  pkg.installed:
    - name: supervisor
  file.managed:
    - name: /etc/supervisor/conf.d/ipcontroller.conf
    - source: salt://ipython/files/controller.conf
    - template: jinja
    - makedirs: true
    - require:
      - pkg: ipcontroller.conf
      - file: controller-log

ipcontroller-update-supervisor:
  module.run:
    - name: supervisord.update
    - watch:
      - file: ipcontroller.conf

ipcontroller-service:
  file.directory:
    - name: /var/log/ipython
  supervisord.running:
    - name: ipcontroller
    - restart: False
    - require:
      - conda: ipcontroller-pkgs
      - file: ipcontroller-service
      - module: ipcontroller-update-supervisor

/srv/salt/ipython/files/copied-ipcontroller-engine.json:
  file.copy:
    - source: /home/dsb/.ipython/profile_default/security/ipcontroller-engine.json
    - force: true
    - user: dsb
    - watch:
      - supervisord: ipcontroller
