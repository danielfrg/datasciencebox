miniconda:
  pyenv.installed:
    - name: miniconda-3.4.2
    - default: True
  cmd.run:
    - name: ln -s /usr/local/pyenv/shims/* /usr/local/bin
    - unless: test -e /usr/local/bin/conda
    - require:
      - pyenv: miniconda
