{%- from 'cdh5/zookeeper/settings.sls' import zk with context %}

/tmp/zk.debug:
  file.managed:
    - contents: |
        myid: {{ zk['myid'] }}
        port: {{ zk['port'] }}
        data_dir: {{ zk['data_dir'] }}
        snap_retain_count: {{ zk['snap_retain_count'] }}
        zookeepers: {{ zk['zookeepers'] }}
        connection_string: {{ zk['connection_string'] }}
