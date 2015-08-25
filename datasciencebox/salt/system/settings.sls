{% set is_vagrant = grains['virtual'] is defined and grains['virtual'] == 'VirtualBox' %}
{% set user = salt['pillar.get']('system:user', 'ubuntu') %}
