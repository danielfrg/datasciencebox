{%- from 'system/settings.sls' import user with context -%}

miniconda-dir:
  cmd.run:
    - name: exit 1
    - unless: test -e /home/{{ user }}/anaconda
    - user: {{ user }}

conda-cmd:
  cmd.run:
    - name: exit 1
    - unless: test -e /home/{{ user }}/anaconda/bin/conda
    - user: {{ user }}
