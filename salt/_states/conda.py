import os


__virtualname__ = 'conda'

def __virtual__():
    '''
    Only load if the conda module is available in __salt__
    '''
    if 'pip.list' in __salt__:
        return __virtualname__
    return False


def managed(name, packages=None, requirements=None, saltenv='base', user=None):
    """
    Create and install python requirements in a conda enviroment
    pip is isntalled by default in the new enviroment

    name : path to the enviroment to be created
    packages : None
        single package or list of packages to install i.e. numpy, scipy=0.13.3, pandas
    requirements : None
        path to a `requirements.txt` file in the `pip freeze` format
    saltenv : 'base'
        Salt environment. Usefull when the name is file using the salt file system
        (e.g. `salt://.../reqs.txt`)
    user
        The user under which to run the commands
    """
    ret = {'name': name, 'changes': {}, 'comment': '', 'result': True}
    comments = []

    # Create virutalenv
    try:
        installation_comment = __salt__['conda.create'](name, user=user)
        if installation_comment.endswith('created'):
            comments.append('Virtual enviroment "%s" created' % name)
        else:
            comments.append('Virtual enviroment "%s" already exists' % name)
    except Exception as e:
        ret['comment'] = e
        ret['result'] = False
        return ret

    # Install packages
    if packages is not None:
        installation_ret = installed(packages, env=name, saltenv=saltenv, user=user)
        ret['result'] = ret['result'] and installation_ret['result']
        comments.append('From list [%s]' % installation_ret['comment'])
        ret['changes'].update(installation_ret['changes'])

    if requirements is not None:
        installation_ret = installed(requirements, env=name, saltenv=saltenv, user=user)
        ret['result'] = ret['result'] and installation_ret['result']
        comments.append('From file [%s]' % installation_ret['comment'])
        ret['changes'].update(installation_ret['changes'])

    ret['comment'] = '. '.join(comments)
    return ret


def installed(name, env, saltenv='base', user=None):
    """
    Installs a single package, list of packages (comma separated) or packages in a requirements.txt

    Checks if the package is already in the environment.
    Check ocurres here so is only needed to `conda list` and `pip freeze` once

    name
        name of the package(s) or path to the requirements.txt
    env : None
        environment name or path where to put the new enviroment
        if None (default) will use the default conda environment (`~/anaconda/bin`)
    saltenv : 'base'
        Salt environment. Usefull when the name is file using the salt file system
        (e.g. `salt://.../reqs.txt`)
    user
        The user under which to run the commands
    """
    ret = {'name': name, 'changes': {}, 'comment': '', 'result': True}

    # Generates packages list
    packages = []
    if os.path.exists(name) or name.startswith('salt://'):
        if name.startswith('salt://'):
            lines = __salt__['cp.get_file_str'](name, saltenv)
            lines = lines.split('\n')
        elif os.path.exists(name):
            f = open(name, mode='r')
            lines = f.readlines()
            f.close()

        for line in lines:
            line = line.strip()
            if line != '' and not line.startswith('#'):
                line = line.split('#')[0].strip()  # Remove inline comments
                packages.append(line)
    else:
        packages = [pkg.strip() for pkg in name.split(',')]

    conda_list = __salt__['conda.list'](env, user=user)

    def extract_info(pkgname):
        pkgname, pkgversion = package, ''
        pkgname, pkgversion = (package.split('==')[0], package.split('==')[1]) if '==' in package else (package, pkgversion)
        pkgname, pkgversion = (package.split('>=')[0], package.split('>=')[1]) if '>=' in package else (pkgname, pkgversion)
        pkgname, pkgversion = (package.split('>')[0], package.split('>=')[1]) if '>' in package else (pkgname, pkgversion)
        return pkgname, pkgversion

    installed, failed, old = 0, 0, 0
    for package in packages:
        pkgname, pkgversion = extract_info(package)
        conda_pkgname = pkgname + ' ' * (26 - len(pkgname)) + pkgversion

        if conda_pkgname not in conda_list:
            installation = __salt__['conda.install'](package, env=env, user=user)
            if installation['retcode'] == 0:
                ret['changes'][package] = 'installed'
                installed += 1
            else:
                ret['changes'][package] = installation
                failed += 1
        else:
            old += 1

    comments = []
    if installed > 0:
        comments.append('{0} installed'.format(installed))
    if failed > 0:
        ret['result'] = False
        comments.append('{0} failed'.format(failed))
    if old > 0:
        comments.append('{0} already installed'.format(old))

    ret['comment'] = ', '.join(comments)
    return ret


def execcmd(cmd, user=None):
    return __salt__['cmd.run_all'](' '.join(cmd), runas=user)
