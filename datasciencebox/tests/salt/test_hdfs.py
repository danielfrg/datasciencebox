import pytest

requests = pytest.importorskip("requests")
hdfs = pytest.importorskip("hdfs")

try:
    from hdfs.client import Client
except ImportError:
    pass

import utils


def setup_module(module):
    utils.invoke('install', 'hdfs')


@utils.remotetest
def test_salt_formulas():
    project = utils.get_test_project()

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['cdh5.hdfs.cluster'], kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)


@utils.remotetest
def test_hdfs_dirs():
    project = utils.get_test_project()
    nn_ip = project.cluster.head.ip

    hdfs = Client('http://%s:50070' % nn_ip)
    assert hdfs

    root_dirs = hdfs.list('/')
    assert 'tmp' in root_dirs
    assert 'user' in root_dirs

    users_dirs = hdfs.list('/user')
    assert 'vagrant' in users_dirs


@utils.remotetest
def test_namenode_ui():
    '''
    Note: Namenode UI uses a lot of javascript requests alone is not good enough
    '''
    project = utils.get_test_project()
    nn_ip = project.cluster.head.ip

    r = requests.get('http://%s:50070/dfshealth.html#tab-overview' % nn_ip)
    assert r.status_code == 200
