import pytest

from hdfs.client import Client

import utils


@utils.vagranttest
def test_namenode():
    project = utils.get_test_project()

    kwargs = {'--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['cdh5.hdfs.cluster'], kwargs=kwargs)
    utils.check_all_true(out)

    nn_ip = project.cluster.master.ip

    hdfs = Client('http://%s:50070' % nn_ip)
    assert hdfs

    root_dirs = hdfs.list('/')
    assert 'tmp' in root_dirs
    assert 'user' in root_dirs

    users_dirs = hdfs.list('/user')
    assert 'vagrant' in users_dirs
