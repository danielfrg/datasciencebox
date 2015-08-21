{%- from 'java/settings.sls' import java with context %}

java:
  pkg.installed:
    - name: {{ java.pkgname }}
  alternatives.set:
    - name: java
    - path: {{ java.bin_path }}/java
