from __future__ import absolute_import, unicode_literals

import os
import subprocess

import click
from fabric.api import settings, run, sudo

from datasciencebox.core.main import Project
from datasciencebox.cli.sync import RsyncHandler, loop as sync_loop


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
    print cmd
    subprocess.call(cmd, shell=True)


def salt_master(project, target, module, args=None, args2=None, user=None):
    host_string = project.dsbfile['user'] + '@' + project.cloud.master.ip
    key_filename = project.dsb['keypair']
    with settings(host_string=host_string, key_filename=key_filename):
        cmd = 'sudo salt {0} {1}'.format(target, module)
        if args:
            cmd += ' ' + args
        if args2:
            cmd += ' ' + args2
        if user:
            cmd += ' user=' + user
        cmd += ' -t 300 --state-output=mixed'
        print cmd
        sudo(cmd)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def main(ctx):
    ctx.obj = {}
    project = Project.from_cwd(cwd=os.getcwd())
    project.read()
    project.read_instances()
    ctx.obj['project'] = project


@main.command('up', short_help='Create the instances')
@click.pass_context
def up(ctx):
    project = ctx.obj['project']
    project.create()
    project.save()
    project.update()


@main.command(short_help='SSH to the Data Science Box')
@click.pass_context
def ssh(ctx):
    project = ctx.obj['project']
    cmd = ['ssh', project.dsbfile['user'] + '@' + project.cloud.master.ip]
    cmd = cmd + ['-i', os.path.expanduser(project.dsbfile['keypair'])]
    cmd = cmd + ['-oStrictHostKeyChecking=no']
    subprocess.call(cmd)


@main.command('salt', short_help='Install salt master and minion(s) via salt-ssh')
@click.pass_context
def install_salt(ctx):
    project = ctx.obj['project']

    pillar_template = '''pillar='{"salt": {"master": {"ip": "%s"}, "minion": {"roles": %s } } }' '''

    # Master
    salt_ssh(project, 'master', 'state.sls', 'salt.master')
    roles = '''["java", "cdh5.hadoop.namenode", "cdh5.zookeeper", "cdh5.hive.metastore", "cdh5.impala.state-store"]'''
    roles = '''["miniconda", "zookeeper", "mesos.master", "namenode", "ipython.notebook", "spark"]'''
    pillars = pillar_template % (project.cloud.master.ip, roles)
    salt_ssh(project, 'master', 'state.sls', 'salt.minion', pillars)

    # Minions
    roles = '''["java", "cdh5.hadoop.datanode", "cdh5.impala.server"]'''
    roles = '''["miniconda", "mesos.slave", "datanode"]'''
    pillars = pillar_template % (project.cloud.master.ip, roles)
    salt_ssh(project, 'minion*', 'state.sls', 'salt.minion', pillars)

    salt_master(project, '*', 'saltutil.sync_all')


@main.command(short_help='rsync salt states and pillar to master')
@click.pass_context
@click.option('--skip', '-s', required=False, is_flag=True, help='Skip initial sync')
@click.option('--continuous', '-c', required=False,  is_flag=True, help='Sync continously based on file system changes')
def sync(ctx, continuous, skip):
    project = ctx.obj['project']

    handler = RsyncHandler()
    handler.project = project
    if not skip:
        handler.sync_all()
    if continuous:
        print 'Waiting for changes on the file system'
        sync_loop(project, handler)


if __name__ == '__main__':
    main()
