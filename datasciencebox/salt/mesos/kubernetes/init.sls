kubernetes-git:
  git.latest:
    - name: https://github.com/kubernetes/kubernetes
    - target: /usr/lib/kubernetes
    - rev: v1.0.3

kube-golang:
  pkg.installed:
    - name: golang

kube-build-essential:
  pkg.installed:
    - name:  build-essential

kubernetes-make:
  cmd.run:
    - name: make
    - cwd: /usr/lib/kubernetes
    - env:
      - KUBERNETES_CONTRIB: mesos
    - require:
      - pkg: kube-golang
      - pkg: kube-build-essential
      - git: kubernetes-git
