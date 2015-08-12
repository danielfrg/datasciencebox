include:
  - users

miniconda-download:
  cmd.run:
    - name: |
        wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
        bash /tmp/miniconda.sh -b -p /home/dsb/anaconda
        /home/dsb/anaconda/bin/conda install pip -y
    - unless: test -e /home/dsb/anaconda
    - cwd: /home/dsb
    - user: dsb
