import pytest

requests = pytest.importorskip("requests")

import utils


pytestmark = pytest.mark.skipif(True, reason='Marathon is currently broken')


def setup_module(module):
    utils.invoke('install', 'marathon')


@utils.remotetest
def test_salt_formulas():
    project = utils.get_test_project()

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['cdh5.zookeeper.cluster'], target='head', kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['mesos.cluster'], kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['mesos.marathon'], target='head', kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)


@utils.remotetest
def test_marathon_ui():
    '''
    Note 1: Marathon UI uses a lot of javascript requests alone is not good enough
    Note 2: Marathon UI does not bing to 0.0.0.0 so need explicit vagrant IP
    '''
    project = utils.get_test_project()
    nn_ip = project.cluster.head.ip
    nn_ip = '10.10.10.100'

    r = requests.get('http://%s:18080/' % nn_ip)
    assert r.status_code == 200
