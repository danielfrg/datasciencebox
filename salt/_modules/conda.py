import os
import pwd

import salt.utils
from salt.exceptions import CommandExecutionError, CommandNotFoundError


def __virtual__():
    return True

__func_alias__ = {
    'list_': 'list'
}


def create(path, user=None):
    """
    Create a conda virutalenv
    """
    cmd = _create_conda_cmd('create', path, ['pip', '--yes', '-q'], user=user)
    ret = _execcmd(cmd, user=user)

    if ret['retcode'] == 0:
        # Virtual enviroment created
        return 'Virtual enviroment "%s" created' % path
    else:
        if ret['stderr'].startswith('Error: prefix already exists:'):
            # Virtual env already exists
            return 'Virtual enviroment "%s" already exists' % path
        else:
            raise salt.exceptions.CommandExecutionError(ret['stderr'])


def install(package, env=None, user=None):
    """
    Install a conda single package in a virutalenv
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
    List the installed packages on an environment
    """
    cmd = _create_conda_cmd('list', env=env, user=user)
    ret = _execcmd(cmd, user=user)
    if ret['retcode'] == 0:
        return ret['stdout']
    else:
        raise 'ERROR: ' + ret['stderr']


def _install_pip(package, env=None, user=None):
    cmd = [os.path.join(_get_env_path(env=env, user=user), 'bin', 'pip'), 'install', '-q', package]
    return _execcmd(cmd, user=user)


def _install_conda(package, env=None, user=None):
    cmd = _create_conda_cmd('install', args=[package, '--yes', '-q'], env=None, user=user)
    return _execcmd(cmd, user=user)


def _create_conda_cmd(conda_cmd, args=None, env=None, user=None):
    cmd = [_get_conda_path(user=user), conda_cmd]
    if env:
        cmd = cmd + ['-n', env]
    if args is not None and args != []:
        cmd.extend(args)
    return cmd


def _get_conda_path(user=None):
    if user:
        return os.path.join(_get_anaconda_dir_path(user=user), 'bin', 'conda')
    return 'conda'


def _get_env_path(env=None, user=None):
    print user, env
    if user:
        if env:
            return os.path.join(_get_anaconda_dir_path(user=user), 'envs', env)
        else:
            return _get_anaconda_dir_path(user=user)


def _get_anaconda_dir_path(user=None):
    if user:
        for u in pwd.getpwall():
            if u.pw_name == user:
                return os.path.join(u.pw_dir, 'anaconda')


def _execcmd(cmd, user=None):
    return __salt__['cmd.run_all'](' '.join(cmd), runas=user)
