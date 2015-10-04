import pytest

import json
from distutils.version import StrictVersion

import utils


def setup_module(module):
    result = utils.invoke('install', 'miniconda')
    assert result.exit_code == 0


@utils.vagranttest
def test_salt_formulas():
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

    # Test env dir
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

    # Test env dir
    kwargs = {'test': 'true', '--out': 'json', '--out-indent': '-1'}
    test = '"test -e /home/vagrant/anaconda/envs/%s"' % env
    out = project.salt('cmd.run_all', args=[test], kwargs=kwargs)
    utils.check_all_cmd_retcode0(out)

    kwargs = {'env': env, '--out': 'json', '--out-indent': '-1'}
    out = project.salt('conda.list', kwargs=kwargs)
    check_pkg(out, 'numpy')
    check_pkg(out, 'numpy', minion='head')
    check_pkg(out, 'numpy', minion='compute')
    check_pkg(out, 'scipy')
    check_pkg(out, 'pandas')


@utils.vagranttest
def test_conda_install():
    env = 'test_conda_install'
    project = utils.get_test_project()
    out = project.salt('cmd.run', args=['"rm -rf /home/vagrant/anaconda/envs/%s"' % env])

    out = project.salt('conda.create', args=[env])

    kwargs = {'env': env, '--out': 'json', '--out-indent': '-1'}
    out = project.salt('conda.list', kwargs=kwargs)
    with pytest.raises(AssertionError):
        check_pkg(out, 'numpy')
    with pytest.raises(AssertionError):
        check_pkg(out, 'scipy')
    with pytest.raises(AssertionError):
        check_pkg(out, 'pandas')

    out = project.salt('conda.install', args=['numpy==1.7.1'], kwargs={'env': env})
    out = project.salt('conda.list', kwargs=kwargs)
    check_pkg(out, 'numpy', version='1.7.1')
    with pytest.raises(AssertionError):
        check_pkg(out, 'scipy')
    with pytest.raises(AssertionError):
        check_pkg(out, 'pandas')

    out = project.salt('conda.install', args=['scipy'], kwargs={'env': env}, target='head')
    out = project.salt('conda.list', kwargs=kwargs)
    check_pkg(out, 'numpy')
    check_pkg(out, 'scipy', minion='head')
    with pytest.raises(AssertionError):
        check_pkg(out, 'scipy', minion='minion-0')
    with pytest.raises(AssertionError):
        check_pkg(out, 'pandas')

    out = project.salt('conda.install', args=['scipy'], kwargs={'env': env})
    out = project.salt('conda.list', kwargs=kwargs)
    check_pkg(out, 'numpy')
    check_pkg(out, 'scipy', minion='head')
    check_pkg(out, 'scipy', minion='minion-0')
    with pytest.raises(AssertionError):
        check_pkg(out, 'pandas')

    out = project.salt('conda.install', args=['pandas'], kwargs=kwargs, target='*')
    out = project.salt('conda.list', kwargs=kwargs)
    check_pkg(out, 'numpy')
    check_pkg(out, 'scipy')
    check_pkg(out, 'pandas')


@utils.vagranttest
def test_conda_install_update_remove():
    env = 'test_conda_install_update_remove'
    project = utils.get_test_project()
    out = project.salt('cmd.run', args=['"rm -rf /home/vagrant/anaconda/envs/%s"' % env])

    out = project.salt('conda.create', args=[env])

    kwargs = {'env': env, '--out': 'json', '--out-indent': '-1'}
    out = project.salt('conda.list', kwargs=kwargs)
    with pytest.raises(AssertionError):
        check_pkg(out, 'boto')
    with pytest.raises(AssertionError):
        check_pkg(out, 'scikit-learn')

    out = project.salt('conda.install', args=['boto==2.7.0'], kwargs={'env': env})
    out = project.salt('conda.list', kwargs=kwargs)
    check_pkg(out, 'boto', version='2.7.0')

    out = project.salt('conda.update', args=['boto'], kwargs={'env': env})
    out = project.salt('conda.list', kwargs=kwargs)
    check_pkg(out, 'boto', version_greater_than='2.7.0')

    out = project.salt('conda.install', args=['scikit-learn'], kwargs={'env': env})
    out = project.salt('conda.list', kwargs=kwargs)
    check_pkg(out, 'scikit-learn')

    out = project.salt('conda.remove',
                       args=['scikit-learn'],
                       kwargs={'env': env},
                       target='minion-0')
    out = project.salt('conda.list', kwargs=kwargs)
    check_pkg(out, 'scikit-learn', minion='head')
    with pytest.raises(AssertionError):
        check_pkg(out, 'scikit-learn', minion='minion-0')

    out = project.salt('conda.remove', args=['scikit-learn'], kwargs={'env': env})
    out = project.salt('conda.list', kwargs=kwargs)
    with pytest.raises(AssertionError):
        check_pkg(out, 'scikit-learn', minion='head')
    with pytest.raises(AssertionError):
        check_pkg(out, 'scikit-learn', minion='minion-0')


def check_pkg(conda_list, package, minion=None, version=None, version_greater_than=None):
    """
    Utility to checks if a package is on the list of packages
    """
    minions = []
    for minion_output in conda_list.split('\n'):
        minions.append(json.loads(minion_output))

    if minion:
        for minion_dict in minions:
            if minion in minion_dict:
                minion_name = minion
                minion_packages = minion_dict.values()[0]
                assert package in minion_packages, "Minion: %s" % minion_name
                if version:
                    assert version == minion_dict[minion_name][package]['version']
    else:
        for minion_dict in minions:
            minion_name = minion_dict.keys()[0]
            minion_packages = minion_dict.values()[0]
            assert package in minion_packages, "Minion: %s" % minion_name
            if version:
                assert version == minion_dict[minion_name][package]['version']
            if version_greater_than:
                version = minion_dict[minion_name][package]['version']
                assert StrictVersion(version) > StrictVersion(version_greater_than)
