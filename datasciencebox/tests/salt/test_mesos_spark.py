import pytest

hdfs = pytest.importorskip("hdfs")
try:
    from hdfs.client import Client
except ImportError:
    pass

import utils


def setup_module(module):
    utils.invoke('install', 'spark')


@utils.vagranttest
def test_salt_formulas():
    project = utils.get_test_project()

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['cdh5.zookeeper.cluster'], target='head', kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['cdh5.hdfs.cluster'], kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['mesos.cluster'], kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['mesos.spark'], kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)


@utils.vagranttest
def test_hdfs_files():
    project = utils.get_test_project()
    head_ip = project.cluster.head.ip
    hdfs = Client('http://%s:50070' % head_ip)

    root_dirs = hdfs.list('/')
    assert 'spark' in root_dirs

    spark_dirs = hdfs.list('/spark')
    assert 'spark-1.4.1-bin-hadoop2.6.tgz' in spark_dirs
