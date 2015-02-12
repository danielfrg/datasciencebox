base:
  'roles:salt-master':
    - match: grain
    - salt.master
