include:
  - users

# If vagrant authorized_keys exists copy to dsb user
# Indicator that its a local vagrant VM
vagrant-keys:
  cmd.run:
    - name: cp /home/vagrant/.ssh/authorized_keys authorized_keys && chown dsb authorized_keys
    - cwd: /home/dsb/.ssh
    - onlyif: test -e /home/vagrant/.ssh/authorized_keys && test ! -e /home/dsb/.ssh/authorized_keys
    - require:
      - sls: users

# If ubuntu authorized_keys exists copy to dsb user
# Indicator that it was created on AWS
ubuntu-keys:
  cmd.run:
    - name: cp /home/ubuntu/.ssh/authorized_keys authorized_keys && chown dsb authorized_keys
    - cwd: /home/dsb/.ssh
    - onlyif: test -e /home/ubuntu/.ssh/authorized_keys && test ! -e /home/dsb/.ssh/authorized_keys
    - require:
      - sls: users
