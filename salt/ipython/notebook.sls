include:
  - miniconda

/home/dsb/notebooks:
  file.directory:
    - user: dsb
    - makedirs: true

notebooks-log-dir:
  file.directory:
    - name: /var/log/ipython
    - makedirs: true

ipython-notebook:
  conda.installed:
    - user: dsb
    - require:
      - sls: miniconda

notebook.conf:
  pkg.installed:
    - name: supervisor
  file.managed:
    - name: /etc/supervisor/conf.d/notebook.conf
    - source: salt://ipython/templates/notebook.conf
    - template: jinja
    - makedirs: true
    - require:
      - pkg: notebook.conf

notebook-update-supervisor:
  module.run:
    - name: supervisord.update
    - watch:
      - file: notebook.conf

notebook-service:
  supervisord.running:
    - name: notebook
    - watch:
      - file: notebook.conf
      - file: notebooks-log-dir
      - conda: ipython-notebook
      - module: notebook-update-supervisor
