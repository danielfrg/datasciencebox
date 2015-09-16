import os
import pwd
import json

import salt.utils


def __virtual__():
    return True


__func_alias__ = {'list_': 'list', 'conda_prefix': 'prefix'}


def conda_prefix(user=None):
    """
    Get the conda prefix for a particular user (~/anaconda)
    If user is None it defaults to /opt/anaconda
    """
    if user == 'root':
        return __salt__['grains.get']('conda:prefix', default='/opt/anaconda')
    else:
        if user is None:
            user = __salt__['pillar.get']('system:user', 'ubuntu')
        for u in pwd.getpwall():
            if u.pw_name == user:
                return os.path.join(u.pw_dir, 'anaconda')


def create(name, packages=None, user=None):
    """
    Create a conda env
    """
    packages = packages or ''
    packages = packages.split(',')
    packages.append('pip')
    args = packages + ['--yes', '-q']
    cmd = _create_conda_cmd('create', args=args, env=name, user=user)
    ret = _execcmd(cmd, user=user, return0=True)

    if ret['retcode'] == 0:
        ret['result'] = True
        ret['comment'] = 'Virtual enviroment "%s" successfully created' % name
    else:
        if ret['stderr'].startswith('Error: prefix already exists:'):
            ret['result'] = True
            ret['comment'] = 'Virtual enviroment "%s" already exists' % name
        else:
            ret['result'] = False
            ret['error'] = salt.exceptions.CommandExecutionError(ret['stderr'])
    return ret


def install(packages, env=None, user=None):
    """
    Install conda packages in a conda env

    Attributes
    ----------
        packages: list of packages comma delimited
    """
    packages = ' '.join(packages.split(','))
    cmd = _create_conda_cmd('install', args=[packages, '--yes', '-q'], env=env, user=user)
    return _execcmd(cmd, user=user)


def list_(env=None, user=None):
    """
    List the installed packages on an environment

    Returns
    -------
        Dictionary: {package: {version: 1.0.0, build: 1 } ... }
    """
    cmd = _create_conda_cmd('list', args=['--json'], env=env, user=user)
    ret = _execcmd(cmd, user=user)
    if ret['retcode'] == 0:
        pkg_list = json.loads(ret['stdout'])
        packages = {}
        for pkg in pkg_list:
            pkg_info = pkg.split('-')
            name, version, build = '-'.join(pkg_info[:-2]), pkg_info[-2], pkg_info[-1]
            packages[name] = {'version': version, 'build': build}
        return packages
    else:
        return ret


def update(packages, env=None, user=None):
    """
    Update conda packages in a conda env

    Attributes
    ----------
        packages: list of packages comma delimited
    """
    packages = ' '.join(packages.split(','))
    cmd = _create_conda_cmd('update', args=[packages, '--yes', '-q'], env=env, user=user)
    return _execcmd(cmd, user=user)


def remove(packages, env=None, user=None):
    """
    Remove conda packages in a conda env

    Attributes
    ----------
        packages: list of packages comma delimited
    """
    packages = ' '.join(packages.split(','))
    cmd = _create_conda_cmd('remove', args=[packages, '--yes', '-q'], env=env, user=user)
    return _execcmd(cmd, user=user, return0=True)


def _create_conda_cmd(conda_cmd, args=None, env=None, user=None):
    """
    Utility to create a valid conda command
    """
    cmd = [_get_conda_path(user=user), conda_cmd]
    if env:
        cmd.extend(['-n', env])
    if args is not None and isinstance(args, list) and args != []:
        cmd.extend(args)
    return cmd


def _get_conda_path(user=None):
    """
    Get the path to the conda exec
    """
    return os.path.join(conda_prefix(user=user), 'bin', 'conda')


def _get_env_path(env=None, user=None):
    if env:
        return os.path.join(conda_prefix(user=user), 'envs', env)
    else:
        return conda_prefix(user=user)


def _execcmd(cmd, user=None, return0=False):
    if return0:
        cmd.append(' || true')
    return __salt__['cmd.run_all'](' '.join(cmd), python_shell=True, runas=user)
