nltk-download:
  cmd.run:
    - name: wget https://s3.amazonaws.com/o360-transfers/nltk_data.tgz -q
    - cwd: /usr/share/
    - unless: test -e /usr/share/nltk_data

nltk-untar:
  cmd.run:
    - name: tar -xzf nltk_data.tgz
    - cwd: /usr/share/
    - unless: test -e /usr/share/nltk_data
    - require:
      - cmd: nltk-download
