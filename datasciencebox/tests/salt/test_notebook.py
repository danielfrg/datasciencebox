import pytest

requests = pytest.importorskip("requests")

import utils


def setup_module(module):
    utils.invoke('install', 'notebook')


@utils.remotetest
def test_salt_formulas():
    project = utils.get_test_project()

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['ipython.notebook'], target='head', kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)


@utils.remotetest
def test_notebook_ui():
    project = utils.get_test_project()

    project = utils.get_test_project()
    head_ip = project.cluster.head.ip

    r = requests.get('http://%s:8888/' % head_ip)
    assert r.status_code == 200
