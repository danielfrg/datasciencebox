import pytest

kazoo = pytest.importorskip("kazoo")
try:
    from kazoo.client import KazooClient
except ImportError:
    pass

import utils


def setup_module(module):
    utils.invoke('install', 'zookeeper')


@utils.remotetest
def test_salt_formulas():
    project = utils.get_test_project()

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['cdh5.zookeeper.cluster'], target='head', kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)


@utils.remotetest
def test_zk_conn():
    project = utils.get_test_project()

    zk_ip = project.cluster.head.ip
    zk = KazooClient(hosts='%s:2181' % zk_ip)
    zk.start()
    assert zk

    children = zk.get_children('/')
    assert 'zookeeper' in children
