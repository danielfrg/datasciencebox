import pytest

import ibis
from hdfs.client import Client


import utils


def setup_module(module):
    utils.invoke('install', 'impala')


@utils.vagranttest
def test_salt_formulas():
    project = utils.get_test_project()
    
    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['cdh5.hdfs.cluster'], kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['cdh5.hive.metastore'], target='master', kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)
    #
    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['cdh5.impala.cluster'], kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)


@utils.vagranttest
def test_hdfs_dirs():
    project = utils.get_test_project()
    master_ip = project.cluster.master.ip
    hdfs = Client('http://%s:50070' % master_ip)

    users_dirs = hdfs.list('/user')
    assert 'hive' in users_dirs
    assert 'impala' in users_dirs

    users_dirs = hdfs.list('/user/hive')
    assert 'warehouse' in users_dirs


@utils.vagranttest
def test_ibis_conn():
    project = utils.get_test_project()

    master_ip = project.cluster.master.ip
    compute_ip = project.cluster.instances[1].ip

    hdfs = ibis.hdfs_connect(host=master_ip, port=50070)
    impala = ibis.impala.connect(compute_ip, hdfs_client=hdfs)
