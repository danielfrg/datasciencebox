from __future__ import absolute_import, unicode_literals

import os
import subprocess

import click
from fabric.api import settings, run, sudo, hide

from datasciencebox.core.project import Project
from datasciencebox.core.sync import RsyncHandler, loop as sync_loop


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def main(ctx):
    ctx.obj = {}
    project = Project.from_dir(path=os.getcwd())
    ctx.obj['project'] = project


@main.command(short_help='Launch instances')
@click.pass_context
def up(ctx):
    click.echo('Creating cluster')
    project = ctx.obj['project']
    project.create_cluster()
    click.echo('Saving settings')
    project.save()
    project.update()


@main.command(short_help='Destroy instances')
@click.pass_context
def destroy(ctx):
    click.echo('Destroying cluster')
    project = ctx.obj['project']
    project.destroy()


@main.command(short_help='SSH to the master node')
@click.pass_context
def ssh(ctx):
    project = ctx.obj['project']
    ip = project.cluster.master.ip
    username = project.settings['USERNAME']
    keypair = os.path.expanduser(project.settings['KEYPAIR'])
    cmd = ['ssh', username + '@' + ip]
    cmd = cmd + ['-i', keypair]
    cmd = cmd + ['-oStrictHostKeyChecking=no']
    click.echo(' '.join(cmd))
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
        click.echo('Syncing salt formulas and pillars')
        handler.sync_all()
    if continuous:
        click.echo('Waiting for changes on the file system')
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
