import pytest

import os

from datasciencebox.core import salt
from datasciencebox.core.project import Project
from datasciencebox.core.settings import Settings
from datasciencebox.core.cloud.cluster import Cluster

settings = Settings()
settings['USERNAME'] = 'me'
settings['KEYPAIR'] = '/home/ubuntu/.ssh/id_rsa'

_ = [{'id': 0, 'ip': '0.0.0.0'}, {'id': 1, 'ip': '1.1.1.1'}, {'id': 2, 'ip': '2.2.2.2'}]
cluster = Cluster.from_list(_, settings)

master_roles = ['master', 'master2', 'conda']
minion_roles = ['minion2', 'conda']
salt.master_roles = master_roles
salt.minion_roles = minion_roles


def test_generate_salt_ssh_master_conf(tmpdir):
    path = tmpdir.dirname
    p = Project(path=path)
    master = salt.generate_salt_ssh_master_conf(p)
    assert master['root_dir'] == os.path.join(p.settings_dir)
    assert master['cachedir'] == os.path.join(p.settings_dir, 'var', 'cache', 'salt')
    assert master['file_roots']['base'] == [os.path.join(p.settings_dir, 'salt')]
    assert master['pillar_roots']['base'] == [os.path.join(p.settings_dir, 'pillar')]


def test_generate_salt_cmd():
    cmd = salt.generate_salt_cmd('*', 'test.ping')
    assert cmd == ['"*"', 'test.ping']

    cmd = salt.generate_salt_cmd('*', 'state.sls', args=['cdh5'])
    assert cmd == ['"*"', 'state.sls', 'cdh5']

    cmd = salt.generate_salt_cmd('*', 'state.sls', args=['cdh5.something', 'arg2'])
    assert cmd == ['"*"', 'state.sls', 'cdh5.something', 'arg2']

    cmd = salt.generate_salt_cmd('*', 'test.ping', kwargs={'user': 'root'})
    assert cmd == ['"*"', 'test.ping', 'user=root']

    cmd = salt.generate_salt_cmd('*', 'test.ping', kwargs={'user': 'root', 'test': True})
    assert cmd == ['"*"', 'test.ping', 'test=True', 'user=root']

    cmd = salt.generate_salt_cmd('*', 'conda.install',
                                 args=['a1', 'a2'],
                                 kwargs={'user': 'root',
                                         'test': True})
    assert cmd == ['"*"', 'conda.install', 'a1', 'a2', 'test=True', 'user=root']


def test_roster_item():
    item = salt.roster_item(cluster.master, mine=False)
    assert item == {'host': '0.0.0.0', 'sudo': True, 'user': 'me', 'priv': '/home/ubuntu/.ssh/id_rsa'}


def test_roster_item_roles():
    item = salt.roster_item(cluster.master, roles=['cdh5', 'conda2'], mine=False)
    assert item == {
        'host': '0.0.0.0',
        'sudo': True,
        'user': 'me',
        'priv': '/home/ubuntu/.ssh/id_rsa',
        'grains': {'roles': ['cdh5', 'conda2']}
    }


def test_generate_roster():
    roster = salt.generate_roster(cluster, mine=False)
    ans = {
        'master': {
            'host': '0.0.0.0',
            'sudo': True,
            'user': 'me',
            'priv': '/home/ubuntu/.ssh/id_rsa',
            'grains': {'roles': master_roles}
        },
        'minion-1': {
            'host': '1.1.1.1',
            'sudo': True,
            'user': 'me',
            'priv': '/home/ubuntu/.ssh/id_rsa',
            'grains': {'roles': minion_roles}
        },
        'minion-2': {
            'host': '2.2.2.2',
            'sudo': True,
            'user': 'me',
            'priv': '/home/ubuntu/.ssh/id_rsa',
            'grains': {'roles': minion_roles}
        },
    }
    assert roster == ans
