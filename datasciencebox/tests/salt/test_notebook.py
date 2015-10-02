import pytest

import requests

import utils

def setup_module(module):
    utils.invoke('install', 'notebook')


@utils.vagranttest
def test_salt_formulas():
    project = utils.get_test_project()

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['ipython.notebook'], target='master', kwargs=kwargs)
    utils.check_all_true(out, none_is_ok=True)


@utils.vagranttest
def test_notebook_ui():
    project = utils.get_test_project()

    project = utils.get_test_project()
    nn_ip = project.cluster.master.ip

    r = requests.get('http://%s:8888/' % nn_ip)
    assert r.status_code == 200
