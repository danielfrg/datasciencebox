include:
  - users

zsh:
  pkg:
    - installed

oh-my-zsh:
  pkg.installed:
    - name: git
  git.latest:
    - name: git://github.com/robbyrussell/oh-my-zsh.git
    - target: /home/dsb/.oh-my-zsh
    - user: dsb
    - require:
      - sls: users
      - pkg: oh-my-zsh

dot_zshrc:
  file.copy:
    - name: /home/dsb/.zshrc
    - source: /home/dsb/.oh-my-zsh/templates/zshrc.zsh-template
    - user: dsb
    - unless: test -e /home/dsb/.zshrc
    - require:
      - git: oh-my-zsh

append-path:
  file.append:
    - name: /home/dsb/.zshrc
    - text: "export PATH=/home/dsb/envs/base/bin:$PATH"
    - user: dsb
    - watch:
      - file: dot_zshrc
