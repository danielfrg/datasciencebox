from __future__ import absolute_import, unicode_literals

import time

import click

from datasciencebox.cli.main import main, sync, log_option
from datasciencebox.core.project import Project
from datasciencebox.core.salt import master_roles, minion_roles


@main.group(short_help='Install packages, applications and more')
@log_option
@click.pass_context
def install(ctx):
    ctx.obj = ctx.obj if ctx.obj else {}


@install.command('miniconda', short_help='Install miniconda in the instances')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@click.option('--target', '-t', required=False, help='Wildcard matching salt minions')
@log_option
@click.pass_context
def install_miniconda(ctx, ssh, target):
    project = Project.from_dir(path=ctx.obj['cwd'])
    project.salt('state.sls', args=['miniconda'], target=target, ssh=ssh)
    if not ssh:
        project.salt('saltutil.sync_all', target=target)


@install.command('salt', short_help='Install salt master and minion(s) via salt-ssh')
@log_option
@click.pass_context
def install_salt(ctx):
    project = Project.from_dir(path=ctx.obj['cwd'])

    pillar_template = """pillar='{"salt": {"master": {"ip": "%s"}, "minion": {"roles": %s } } }' """

    click.echo('Installing salt master in the head')
    project.salt('state.sls', args=['salt.master'], target='master', ssh=True)

    click.echo('Installing salt minion in the head')
    roles_txt = ['"%s"' % role for role in master_roles]
    roles_txt = '[%s]' % ', '.join(roles_txt)
    pillars = pillar_template % (project.cluster.master.ip, roles_txt)
    project.salt('state.sls', args=['salt.minion', pillars], target='master', ssh=True)

    if len(project.cluster) > 1:
        click.echo('Installing salt minion in the compute nodes')
        roles_txt = ['"%s"' % role for role in minion_roles]
        roles_txt = '[%s]' % ', '.join(roles_txt)
        pillars = pillar_template % (project.cluster.master.ip, roles_txt)
        project.salt('state.sls', args=['salt.minion', pillars], target='minion*', ssh=True)

    click.echo('Syncing formulas')
    ctx.invoke(sync)


@install.command('pkg', short_help='Install a package using system package manager')
@click.argument('pkg', required=True)
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@click.option('--target', '-t', required=False, help='Wildcard matching salt minions')
@log_option
@click.pass_context
def install_pkg(ctx, pkg, ssh, target):
    project = Project.from_dir(path=ctx.obj['cwd'])
    args = [pkg]
    project.salt('pkg.install', args=args, target=target, ssh=ssh)


@install.command('conda', short_help='Install conda package')
@click.argument('pkg', required=True)
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@click.option('--target', '-t', required=False, help='Wildcard matching salt minions')
@log_option
@click.pass_context
def install_conda(ctx, pkg, ssh, target):
    project = Project.from_dir(path=ctx.obj['cwd'])
    project.salt('conda.install', args=[pkg], kwargs={'user': project.settings['USERNAME']}, target=target, ssh=ssh)


@install.command('notebook', short_help='Install ipython notebook in the master')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@log_option
@click.pass_context
def install_notebook(ctx, ssh):
    project = Project.from_dir(path=ctx.obj['cwd'])
    project.salt('state.sls', args=['ipython.notebook'], target='master', ssh=ssh)


@install.command('hdfs', short_help='Install hdfs in the cluster')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@log_option
@click.pass_context
def install_hdfs(ctx, ssh):
    project = Project.from_dir(path=ctx.obj['cwd'])
    project.salt('state.sls', args=['cdh5.hdfs.cluster'], target='*', ssh=ssh)


@install.command('mesos', short_help='Install mesos in the cluster')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@log_option
@click.pass_context
def install_mesos(ctx, ssh):
    project = Project.from_dir(path=ctx.obj['cwd'])
    project.salt('state.sls', args=['cdh5.zookeeper'], target='master', ssh=ssh)
    project.salt('state.sls', args=['mesos.cluster'], target='*', ssh=ssh)


@install.command('marathon', short_help='Install mesos in the cluster')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@log_option
@click.pass_context
def install_marathon(ctx, ssh):
    project = Project.from_dir(path=ctx.obj['cwd'])
    project.salt('state.sls', args=['mesos.marathon'], target='master', ssh=ssh)


@install.command('spark', short_help='Install spark in the master')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@log_option
@click.pass_context
def install_spark(ctx, ssh):
    project = Project.from_dir(path=ctx.obj['cwd'])
    project.salt('state.sls', args=['mesos.spark'], target='master', ssh=ssh)
