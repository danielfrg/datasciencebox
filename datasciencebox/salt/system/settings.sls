{% set is_vagrant = grains['virtual'] is defined and grains['virtual'] == 'VirtualBox' %}
