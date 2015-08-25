{%- from 'system/settings.sls' import user with context -%}

miniconda-download:
  cmd.run:
    - name: |
        wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
        bash /tmp/miniconda.sh -b -p /home/{{ user }}/anaconda
        /home/{{ user }}/anaconda/bin/conda install pip -y
    - unless: test -e /home/{{ user }}/anaconda
    - cwd: /home/{{ user }}
    - user: {{ user }}
