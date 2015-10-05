import pytest

hdfs = pytest.importorskip("hdfs")
try:
    from hdfs.client import Client
except ImportError:
    pass

ibis = pytest.importorskip("ibis")

import utils


def setup_module(module):
    utils.invoke('install', 'impala')


@utils.remotetest
def test_salt_formulas():
    project = utils.get_test_project()

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['cdh5.hdfs.cluster'], kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['cdh5.hive.metastore'], target='head', kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)
    #
    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['cdh5.impala.cluster'], kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)


@utils.remotetest
def test_hdfs_dirs():
    project = utils.get_test_project()
    head_ip = project.cluster.head.ip
    hdfs = Client('http://%s:50070' % head_ip)

    users_dirs = hdfs.list('/user')
    assert 'hive' in users_dirs
    assert 'impala' in users_dirs

    users_dirs = hdfs.list('/user/hive')
    assert 'warehouse' in users_dirs


@utils.remotetest
def test_ibis_conn():
    project = utils.get_test_project()

    head_ip = project.cluster.head.ip
    compute_ip = project.cluster.instances[1].ip

    hdfs = ibis.hdfs_connect(host=head_ip, port=50070)
    impala = ibis.impala.connect(compute_ip, hdfs_client=hdfs)
