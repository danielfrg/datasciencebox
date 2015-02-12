from __future__ import unicode_literals
import os

BASE_DIR = os.path.expanduser('~/.datasciencebox')
CLUSTERS_DIR = os.path.join(BASE_DIR, 'clusters')
PROFILES_DIR = os.path.join(BASE_DIR, 'profiles')
PROVIDERS_DIR = os.path.join(BASE_DIR, 'providers')

this_file_path = os.path.realpath(__file__)
SALT_STATES_DIR = os.path.realpath(os.path.join(this_file_path, '..', '..', '..', 'salt'))
SALT_PILLAR_DIR = os.path.realpath(os.path.join(this_file_path, '..', '..', '..', 'pillar'))

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_dirs():
    create_dir(CLUSTERS_DIR)
    create_dir(PROFILES_DIR)
    create_dir(PROVIDERS_DIR)

create_dirs()
