from __future__ import absolute_import, unicode_literals

import os
import subprocess

import click
from fabric.api import settings, run, sudo, hide

from datasciencebox.core.project import Project
from datasciencebox.core.sync import RsyncHandler, loop as sync_loop


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

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0 or err:
        raise Exception(err)
    return proc.returncode, out, err


def salt_master(project, target, module, args=None, args2=None, user=None):
    host_string = project.dsbfile['user'] + '@' + project.cluster.master.ip
    key_filename = project.dsbfile['keypair']
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


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def main(ctx):
    ctx.obj = {}
    project = Project.from_cwd(cwd=os.getcwd())
    ctx.obj['project'] = project


@main.command(short_help='Create instances')
@click.pass_context
def up(ctx):
    project = ctx.obj['project']
    project.create()
    project.save()
    project.update()


@main.command(short_help='Destroy instances')
@click.pass_context
def destroy(ctx):
    project = ctx.obj['project']
    project.destroy()


@main.command(short_help='SSH to the Data Science Box')
@click.pass_context
def ssh(ctx):
    project = ctx.obj['project']
    cmd = ['ssh', project.dsbfile['user'] + '@' + project.cluster.master.ip]
    cmd = cmd + ['-i', os.path.expanduser(project.dsbfile['keypair'])]
    cmd = cmd + ['-oStrictHostKeyChecking=no']
    subprocess.call(cmd)


@main.command(short_help='Sync salt states and pillar to master')
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


@main.command(short_help='Update (overwriting) project settings. Careful.')
@click.pass_context
def update(ctx):
    project = ctx.obj['project']
    project.update()


from datasciencebox.cli.install import *
from datasciencebox.cli.open import *

if __name__ == '__main__':
    main()
