from __future__ import unicode_literals

import pytest

import os

from datasciencebox.core import salt
from datasciencebox.core.project import Project
from datasciencebox.core.cloud.cluster import Cluster
from datasciencebox.core.cloud.instance import Instance

cluster = Cluster()
cluster.instances.append(Instance(ip='0.0.0.0', username='me', keypair='/home/ubuntu/.ssh/id_rsa'))
cluster.instances.append(Instance(ip='1.1.1.1:2222',
                                  username='ubuntu',
                                  keypair='/home/ubuntu/.ssh/id_rsa2'))
cluster.instances.append(Instance(ip='2.2.2.2',
                                  port='3333',
                                  username='centos',
                                  keypair='/home/ubuntu/.ssh/id_rsa3'))

head_roles = ['head', 'head2', 'conda']
compute_roles = ['minion2', 'conda']
salt.HEAD_ROLES = head_roles
salt.COMPUTE_ROLES = compute_roles


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

    cmd = salt.generate_salt_cmd('*',
                                 'conda.install',
                                 args=['a1', 'a2'],
                                 kwargs={'user': 'root',
                                         'test': True})
    assert cmd == ['"*"', 'conda.install', 'a1', 'a2', 'test=True', 'user=root']


def test_roster_item():
    item = salt.roster_item(cluster.head, mine=False)
    assert item == {
        'host': '0.0.0.0',
        'port': 22,
        'sudo': True,
        'user': 'me',
        'priv': '/home/ubuntu/.ssh/id_rsa'
    }


def test_roster_item_with_roles():
    item = salt.roster_item(cluster.head, roles=['cdh5', 'conda2'], mine=False)
    assert item == {
        'host': '0.0.0.0',
        'port': 22,
        'sudo': True,
        'user': 'me',
        'priv': '/home/ubuntu/.ssh/id_rsa',
        'grains': {'roles': ['cdh5', 'conda2']}
    }


def test_generate_roster():
    roster = salt.generate_roster(cluster, mine=False)
    ans = {
        'head': {
            'host': '0.0.0.0',
            'port': 22,
            'sudo': True,
            'user': 'me',
            'priv': '/home/ubuntu/.ssh/id_rsa',
            'grains': {'roles': head_roles}
        },
        'compute-1': {
            'host': '1.1.1.1',
            'port': 2222,
            'sudo': True,
            'user': 'ubuntu',
            'priv': '/home/ubuntu/.ssh/id_rsa2',
            'grains': {'roles': compute_roles}
        },
        'compute-2': {
            'host': '2.2.2.2',
            'port': 3333,
            'sudo': True,
            'user': 'centos',
            'priv': '/home/ubuntu/.ssh/id_rsa3',
            'grains': {'roles': compute_roles}
        },
    }
    assert roster == ans
