from __future__ import absolute_import, unicode_literals

import subprocess

from fabric.api import settings, run, sudo, hide


def salt_ssh(project, target, module, args=None, args2=None):
    roster_file = '--roster-file=%s' % project.roster_path
    config_dir = '--config-dir=%s' % project.salt_ssh_config_dir
    cmd = ['salt-ssh', roster_file, config_dir, '--ignore-host-keys', target, module]
    if args:
        cmd = cmd + [args]
    if args2:
        cmd = cmd + [args2]

    cmd = cmd + ['--state-output=mixed']
    cmd = ' '.join(cmd)
    print(cmd)

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0 or err:
        raise Exception(err)
    print out
    return proc.returncode, out, err


def salt_master(project, target, module, args=None, args2=None, user=None):
    ip = project.cluster.master.ip
    username = project.settings['USERNAME']
    host_string = username + '@' + ip
    key_filename = project.settings['KEYPAIR']
    with hide('running', 'stdout', 'stderr'):
        with settings(host_string=host_string, key_filename=key_filename):
            cmd = 'sudo salt {0} {1}'.format(target, module)
            if args:
                cmd += ' ' + args
            if args2:
                cmd += ' ' + args2
            if user:
                cmd += ' user=' + user
            cmd += ' -t 300 --state-output=mixed'
            # print cmd
            out = sudo(cmd)
            print out
