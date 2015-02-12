import os
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
    cmd = _create_conda_cmd('create', path, ['pip', '--yes', '-q'])
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


def install(package, env, user=None):
    """
    Install a conda single package in a virutalenv
    """
    if package.startswith('git'):
        return _install_pip(package, env, user=user)

    ret = _install_conda(package, env, user=user)
    if ret['retcode'] == 0:
        return ret
    elif 'Error: No packages found in current' in ret['stderr']:
        ret = _install_pip(package, env, user=user)
        return ret


def list_(env, user=None):
    """
    List the installed packages on an environment
    """
    cmd = _create_conda_cmd('list', env)
    ret = _execcmd(cmd, user=user)
    if ret['retcode'] == 0:
        return ret['stdout']
    else:
        raise 'ERROR: ' + ret['stderr']


def _install_pip(package, env, user=None):
    cmd = [os.path.join(env, 'bin', 'pip'), 'install', '-q', package]
    return _execcmd(cmd, user=user)


def _install_conda(package, env, user=None):
    cmd = _create_conda_cmd('install', env, [package, '--yes', '-q'])
    return _execcmd(cmd, user=user)


def _create_conda_cmd(conda_cmd, env, args=None):
    cmd = ['conda', conda_cmd, '-p', env]
    if args is not None and args != []:
        cmd.extend(args)
    return cmd


def _execcmd(cmd, user=None):
    return __salt__['cmd.run_all'](' '.join(cmd), runas=user)
