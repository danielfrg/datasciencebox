{% set java = salt['grains.filter_by']({
    'Debian': {
        'pkgname': 'openjdk-7-jre-headless',
        'java_home': '/usr/lib/jvm/java-7-openjdk-amd64/jre',
        'bin_path': '/usr/lib/jvm/java-7-openjdk-amd64/jre/bin',
    },
    'RedHat': {
        'pkgname': 'java-1.7.0-openjdk',
        'java_home': '/usr/lib/jvm/jre-1.7.0-openjdk.x86_64',
        'bin_path': '/usr/lib/jvm/jre-1.7.0-openjdk.x86_64/bin',
    },
}, merge=salt['pillar.get']('java:lookup')) %}
