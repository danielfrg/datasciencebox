kudu.list:
  file.managed:
    - name: /etc/apt/sources.list.d/kudu.list
    - source: http://archive.cloudera.com/beta/kudu/ubuntu/{{ grains["lsb_distrib_codename"] }}/amd64/kudu/cloudera.list
    - source_hash: md5=42ddd8e3c60de424de4e0ab527531e45
