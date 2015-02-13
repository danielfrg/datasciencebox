key:
  cmd.run:
    - name: apt-key adv --keyserver keyserver.ubuntu.com --recv E56151BF

mesos-apt:
  file.managed:
    - name: /etc/apt/sources.list.d/mesosphere.list
    - contents: deb http://repos.mesosphere.io/{{ grains["lsb_distrib_id"] | lower() }} {{ grains["lsb_distrib_codename"] | lower() }} main
    - require:
      - cmd: key
  module.wait:
    - name: pkg.refresh_db
    - watch:
      - file: mesos-apt

mesos:
  pkg.installed:
    - name: mesos
    - require:
      - module: mesos-apt
