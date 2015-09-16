import pytest

import utils


@utils.vagranttest
def test_miniconda():
    result = utils.invoke('install', 'miniconda')
    assert result.exit_code == 0

    project = utils.get_test_project()
    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    out = project.salt('state.sls', args=['miniconda.status'], kwargs=kwargs)
    utils.check_all_true(out)
