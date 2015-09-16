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


@utils.vagranttest
def test_conda_create():
    env = 'test_conda_create'
    project = utils.get_test_project()
    out = project.salt('cmd.run', args=['"rm -rf /home/vagrant/anaconda/envs/%s"' % env])

    out = project.salt('conda.create', args=[env])

    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    test = '"test -e /home/vagrant/anaconda/envs/%s"' % env
    out = project.salt('cmd.run_all', args=[test], kwargs=kwargs)
    utils.check_all_cmd_retcode0(out)


@utils.vagranttest
def test_conda_create_w_pkgs():
    import re
    from collections import Counter
    env = 'test_conda_create_w_pkgs'
    project = utils.get_test_project()
    out = project.salt('cmd.run', args=['"rm -rf /home/vagrant/anaconda/envs/%s"' % env])

    kwargs = {'packages': 'numpy,scipy,pandas'}
    out = project.salt('conda.create', args=[env], kwargs=kwargs)

    kwargs = {'env': env}
    out = project.salt('conda.list', kwargs=kwargs)
    assert Counter(re.findall(r"numpy+", out))['numpy'] == 2
    assert Counter(re.findall(r"scipy+", out))['scipy'] == 2
    assert Counter(re.findall(r"pandas+", out))['pandas'] == 2


@utils.vagranttest
def test_conda_install_update_remove():
    import re
    from collections import Counter
    env = 'test_conda_install_update_remove'
    project = utils.get_test_project()
    out = project.salt('cmd.run', args=['"rm -rf /home/vagrant/anaconda/envs/%s"' % env])

    kwargs = {'packages': 'numpy,scipy,pandas'}
    out = project.salt('conda.create', args=[env])

    kwargs = {'env': env}
    out = project.salt('conda.list', kwargs=kwargs)
    assert Counter(re.findall(r"numpy+", out))['numpy'] == 0
    assert Counter(re.findall(r"scipy+", out))['scipy'] == 0
    assert Counter(re.findall(r"pandas+", out))['pandas'] == 0

    out = project.salt('conda.install', args=['numpy==1.7'], kwargs=kwargs)
    out = project.salt('conda.list', kwargs=kwargs)
    assert Counter(re.findall(r"numpy+", out))['numpy'] == 2
    assert Counter(re.findall(r"scipy+", out))['scipy'] == 0
    assert Counter(re.findall(r"pandas+", out))['pandas'] == 0

    out = project.salt('conda.install', args=['scipy'], kwargs=kwargs, target='master')
    out = project.salt('conda.list', kwargs=kwargs)
    assert Counter(re.findall(r"numpy+", out))['numpy'] == 2
    assert Counter(re.findall(r"scipy+", out))['scipy'] == 1
    assert Counter(re.findall(r"pandas+", out))['pandas'] == 0

    out = project.salt('conda.install', args=['pandas'], kwargs=kwargs, target='*')
    out = project.salt('conda.list', kwargs=kwargs)
    assert Counter(re.findall(r"numpy+", out))['numpy'] == 2
    assert Counter(re.findall(r"scipy+", out))['scipy'] == 1
    assert Counter(re.findall(r"pandas+", out))['pandas'] == 2
