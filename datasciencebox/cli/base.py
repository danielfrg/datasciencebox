from __future__ import absolute_import, unicode_literals
import os
import sys
import subprocess

import click

from datasciencebox.cli.main import cli, default_options
from datasciencebox.core.sync import RsyncHandler, loop as sync_loop


@cli.command(short_help='Launch instances')
@click.option('--salt/--no-salt', default=True, required=False, help='Whether to install salt')
@default_options
@click.pass_context
def up(ctx, salt):
    project = ctx.obj['project']

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
        click.echo('Installing salt (master mode)')
        from datasciencebox.cli.install import install_salt
        ctx.invoke(install_salt)


@cli.command(short_help='Destroy instances')
@click.option('--force',
              '-f',
              is_flag=True,
              default=False,
              help='Don\'t ask questions, assume yes.')
@default_options
@click.pass_context
def destroy(ctx, force):
    if force or click.confirm('Are you sure you want to destroy the cluster?'):
        click.echo('Destroying cluster')
        project = ctx.obj['project']
        project.destroy()
        click.echo('Cluster destroyed')
    else:
        click.echo('Nothing happened')


@cli.command(short_help='Execute a salt module')
@click.argument('target')
@click.argument('module')
@click.argument('args', required=False, nargs=-1)
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@default_options
@click.pass_context
def salt(ctx, target, module, args, ssh):
    project = ctx.obj['project']
    out = project.salt(module, args=args, target=target, ssh=ssh)
    click.echo(out)


@cli.command(short_help='Execute a salt module')
@click.argument('command')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@default_options
@click.pass_context
def cmd(ctx, command, ssh):
    project = ctx.obj['project']
    args = ['"' + command + '"']
    out = project.salt('cmd.run', args=args, ssh=ssh)
    click.echo(out)


@cli.command(short_help='SSH to the head node')
@click.argument('node', required=False, default=0)
@default_options
@click.pass_context
def ssh(ctx, node):
    project = ctx.obj['project']
    node = project.cluster.instances[node]
    ip = node.ip
    username = node.username
    keypair = os.path.expanduser(node.keypair)
    cmd = ['ssh', username + '@' + ip]
    cmd = cmd + ['-i', keypair]
    cmd = cmd + ['-oStrictHostKeyChecking=no']
    cmd = cmd + ['-p %i' % node.port]
    click.echo(' '.join(cmd))
    subprocess.call(cmd)


@cli.command(short_help='Sync salt states and pillar to the head node')
@click.option('--skip', '-s', required=False, is_flag=True, help='Skip initial sync')
@click.option('--continuous',
              '-c',
              required=False,
              is_flag=True,
              help='Sync continously based on file system changes')
@default_options
@click.pass_context
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


@cli.command(short_help='Update (overwriting) project settings and salt formulas')
@default_options
@click.pass_context
def update(ctx):
    project = ctx.obj['project']
    project.update()
