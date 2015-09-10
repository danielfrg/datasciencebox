from __future__ import absolute_import, unicode_literals
import os
import sys
import subprocess

import click

from datasciencebox.cli.main import main, log_option
from datasciencebox.core.project import Project
from datasciencebox.core.sync import RsyncHandler, loop as sync_loop


@main.command(short_help='Launch instances')
@click.option('--salt/--no-salt', default=True, required=False, help='Whether to install salt')
@log_option
@click.pass_context
def up(ctx, salt):
    project = Project.from_dir(path=ctx.obj['cwd'])

    click.echo('Creating cluster')
    project.create_cluster()

    click.echo('Creating metadata')
    project.save_instances()
    project.update()

    click.echo('Checking SSH Connection')
    ssh_status = project.cluster.check_ssh()
    if all(ssh_status.values()):
        click.echo('SSH connection to all nodes OK')
    else:
        click.echo('SSH connection to some nodes did not work.', err=True)
        click.echo('This might be just the cloud provider being slow, wait a while and try again',
                   err=True)
        click.echo(ssh_status, err=True)
        sys.exit(1)

    if salt:
        click.echo('Installing salt (master)')
        ctx.invoke(main.install_salt)


@main.command(short_help='Destroy instances')
@log_option
@click.pass_context
def destroy(ctx):
    click.echo('Destroying cluster')
    project = Project.from_dir(path=ctx.obj['cwd'])
    project.destroy()


@main.command(short_help='Execute a salt module')
@click.argument('target')
@click.argument('module')
@click.argument('args', required=False, nargs=-1)
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@log_option
@click.pass_context
def salt(ctx, target, module, args, ssh):
    project = Project.from_dir(path=ctx.obj['cwd'])
    project.salt(module, args=args, target=target, ssh=ssh)


@main.command(short_help='Execute a salt module')
@click.argument('command')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@log_option
@click.pass_context
def cmd(ctx, command, ssh):
    project = Project.from_dir(path=ctx.obj['cwd'])
    args = ['"' + command + '"']
    project.salt('cmd.run', args=args, ssh=ssh)


@main.command(short_help='SSH to the master node')
@click.argument('node', required=False, default=0)
@log_option
@click.pass_context
def ssh(ctx, node):
    project = Project.from_dir(path=ctx.obj['cwd'])
    node = project.cluster.instances[node]
    ip = node.ip
    username = node.username
    keypair = os.path.expanduser(node.keypair)
    cmd = ['ssh', username + '@' + ip]
    cmd = cmd + ['-i', keypair]
    cmd = cmd + ['-oStrictHostKeyChecking=no']
    click.echo(' '.join(cmd))
    subprocess.call(cmd)


@main.command(short_help='Sync salt states and pillar to master')
@click.option('--skip', '-s', required=False, is_flag=True, help='Skip initial sync')
@click.option('--continuous',
              '-c',
              required=False,
              is_flag=True,
              help='Sync continously based on file system changes')
@log_option
@click.pass_context
def sync(ctx, continuous, skip):
    project = Project.from_dir(path=ctx.obj['cwd'])

    handler = RsyncHandler()
    handler.project = project
    if not skip:
        click.echo('Syncing salt formulas and pillars')
        handler.sync_all()
    if continuous:
        click.echo('Waiting for changes on the file system')
        sync_loop(project, handler)


@main.command(short_help='Update (overwriting) project settings and salt formulas')
@log_option
@click.pass_context
def update(ctx):
    project = Project.from_dir(path=ctx.obj['cwd'])
    project.update()
