{%- from 'java/settings.sls' import java with context %}

{%- if java.source_url is defined %}

include:
  - java.env

{{ java.prefix }}:
  file.directory:
    - user: root
    - group: root
    - mode: 755
    - makedirs: True

unpack-jdk-tarball:
  cmd.run:
    - name: curl {{ java.dl_opts }} '{{ java.source_url }}' | tar xz --no-same-owner
    - cwd: {{ java.prefix }}
    - unless: test -d {{ java.java_real_home }}
    - require:
      - file: {{ java.prefix }}
  alternatives.install:
    - name: java-home-link
    - link: {{ java.java_home }}
    - path: {{ java.java_real_home }}
    - priority: 30

# /usr/java/default:
#   file.symlink:
#     - target: {{ java.java_real_home }}
#     - makedirs: true

{%- endif %}
