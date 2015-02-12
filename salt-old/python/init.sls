include:
  - users
  - conda
  - python.nltk

base:
  pkg.installed:
    - names:
      - git
      - build-essential
  conda.managed:
    - name: /home/dsb/envs/base
    - requirements: salt://python/requirements.txt
    - user: dsb
    - require:
      - pkg: base
      - sls: conda
      - sls: users
