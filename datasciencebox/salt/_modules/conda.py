import os
import pwd

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


def install(package, env=None, user=None):
    """
    Install a single package in a conda env
    If package is not found in the default conda channel it defaults to pip (pypi)
    """
    if package.startswith('git'):
        return _install_pip(package, env=env, user=user)

    ret = _install_conda(package, env=env, user=user)
    if ret['retcode'] == 0:
        return ret
    elif 'Error: No packages found in current' in ret['stderr']:
        ret = _install_pip(package, env=env, user=user)
        return ret


def list_(env=None, user=None):
    """
    List the installed packages on an environment (big string)
    """
    cmd = _create_conda_cmd('list', env=env, user=user)
    ret = _execcmd(cmd, user=user)
    if ret['retcode'] == 0:
        return ret['stdout']
    else:
        raise Exception(ret['stderr'])


def _install_conda(package, env=None, user=None):
    cmd = _create_conda_cmd('install', args=[package, '--yes', '-q'], env=env, user=user)
    return _execcmd(cmd, user=user)


def _create_conda_cmd(conda_cmd, args=None, env=None, user=None):
    cmd = [_get_conda_path(user=user), conda_cmd]
    if env:
        cmd.extend(['-n', env])
    if args is not None and isinstance(args, list) and args != []:
        cmd.extend(args)
    return cmd


def _get_conda_path(user=None):
    return os.path.join(conda_prefix(user=user), 'bin', 'conda')


def _install_pip(package, env=None, user=None):
    cmd = [_get_pip_path(env=env, user=user), 'install', '-q', package]
    return _execcmd(cmd, user=user)


def _get_pip_path(env=None, user=None):
    return os.path.join(_get_env_path(env=env, user=user), 'bin', 'pip')


def _get_env_path(env=None, user=None):
    if env:
        return os.path.join(conda_prefix(user=user), 'envs', env)
    else:
        return conda_prefix(user=user)


def _execcmd(cmd, user=None, return0=False):
    if return0:
        cmd.append(' || true')
    return __salt__['cmd.run_all'](' '.join(cmd), python_shell=True, runas=user)
