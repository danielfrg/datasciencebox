"""
Module that contains salt utilities
All functions here should return dictionaries or object no IO
"""
from __future__ import absolute_import, unicode_literals

import os
import subprocess

from fabric.api import settings, sudo, hide

from datasciencebox.core.logger import getLogger
logger = getLogger()

master_roles = ['miniconda', 'zookeeper', 'mesos.master', 'hdfs.namenode', 'ipython.notebook',
                'spark', 'hive.metastore', 'impala.state-store']
minion_roles = ['miniconda', 'mesos.slave', 'hdfs.datanode', 'impala.server']


def generate_salt_ssh_master_conf(project):
    conf = {}
    conf['file_roots'] = {'base': [project.salt_dir]}
    conf['pillar_roots'] = {'base': [project.pillar_dir]}
    conf['root_dir'] = project.settings_dir
    conf['cachedir'] = os.path.join(project.settings_dir, 'var', 'cache', 'salt')
    return conf


def generate_salt_cmd(target, module, args=None, kwargs=None):
    """
    Generates a command (the arguments) for the `salt` or `salt-ssh` CLI
    """
    args = args or []
    kwargs = kwargs or {}
    target = target or '*'
    target = '"%s"' % target
    cmd = [target, module]
    for arg in args:
        cmd.append(arg)
    for key in kwargs:
        cmd.append('{0}={1}'.format(key, kwargs[key]))
    return cmd


def roster_item(instance, roles=None, mine=True):
    ret = {}
    ret['host'] = instance.ip
    ret['user'] = instance.username
    ret['priv'] = instance.keypair
    ret['sudo'] = True

    grains = {}
    if roles:
        grains['roles'] = roles
    if grains:
        ret['grains'] = grains

    if mine:
        ret['mine_interval'] = 2
        ret['mine_functions'] = {
            'network.get_hostname': [],
            'network.interfaces': [],
            'network.ip_addrs': []
        }

    return ret


def generate_roster(cluster, mine=True):
    ret = {}
    ret['master'] = roster_item(cluster.instances[0], roles=master_roles, mine=mine)
    for i, instance in enumerate(cluster.instances[1:]):
        ret['minion-%i' % (i + 1)] = roster_item(instance, roles=minion_roles, mine=mine)
    return ret


def salt_ssh(project, target, module, args=None, kwargs=None):
    """
    Execute a `salt-ssh` command
    """
    cmd = ['salt-ssh']
    cmd.extend(generate_salt_cmd(target, module, args, kwargs))
    cmd.append('--state-output=mixed')
    cmd.append('--roster-file=%s' % project.roster_path)
    cmd.append('--config-dir=%s' % project.salt_ssh_config_dir)
    cmd.append('--ignore-host-keys')
    cmd.append('--force-color')
    cmd = ' '.join(cmd)
    logger.debug('salt-ssh cmd: %s' % cmd)

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0 or err:
        raise Exception(err)
    print(out + err)
    return out + err


def salt_master(project, target, module, args=None, kwargs=None):
    """
    Execute a `salt` command in the head node
    """
    ip = project.cluster.master.ip
    username = project.settings['USERNAME']
    host_string = username + '@' + ip
    key_filename = project.settings['KEYPAIR']
    with hide('running', 'stdout', 'stderr'):
        with settings(host_string=host_string, key_filename=key_filename):
            cmd = ['salt']
            cmd.extend(generate_salt_cmd(target, module, args, kwargs))
            cmd.append('--timeout=300')
            cmd.append('--state-output=mixed')
            cmd = ' '.join(cmd)
            logger.debug('salt cmd: %s' % cmd)

            out = sudo(cmd)
            print(out)
            return out
