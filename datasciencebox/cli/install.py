from __future__ import absolute_import, unicode_literals

import click

from datasciencebox.cli.main import cli, default_options
from datasciencebox.core.salt import HEAD_ROLES, COMPUTE_ROLES


@cli.group(short_help='Install packages, applications and more')
@click.pass_context
def install(ctx):
    pass


@install.command('miniconda', short_help='Install miniconda in the instances')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@click.option('--target', '-t', required=False, help='Wildcard matching salt minions')
@default_options
@click.pass_context
def install_miniconda(ctx, ssh, target):
    project = ctx.obj['project']
    out = project.salt('state.sls', args=['miniconda'], target=target, ssh=ssh)
    click.echo(out)
    if not ssh:
        out = project.salt('saltutil.sync_all', target=target)
        click.echo(out)


@install.command('salt', short_help='Install salt master and minion(s) via salt-ssh')
@default_options
@click.pass_context
def install_salt(ctx):
    project = ctx.obj['project']

    pillar_template = """pillar='{"salt": {"master": {"ip": "%s"}, "minion": {"roles": %s } } }' """

    click.echo('Installing salt-master in the head')
    out = project.salt('state.sls', args=['salt.master'], target='head', ssh=True)
    click.echo(out)

    click.echo('Installing salt-minion in the head')
    roles_txt = ['"%s"' % role for role in HEAD_ROLES]
    roles_txt = '[%s]' % ', '.join(roles_txt)
    pillars = pillar_template % (project.cluster.head.ip, roles_txt)
    out = project.salt('state.sls', args=['salt.minion', pillars], target='head', ssh=True)
    click.echo(out)

    if len(project.cluster) > 1:
        click.echo('Installing salt-minion in the compute nodes')
        roles_txt = ['"%s"' % role for role in COMPUTE_ROLES]
        roles_txt = '[%s]' % ', '.join(roles_txt)
        pillars = pillar_template % (project.cluster.head.ip, roles_txt)
        out = project.salt('state.sls', args=['salt.minion', pillars], target='compute-*', ssh=True)
        click.echo(out)

    click.echo('Syncing formulas')
    from datasciencebox.cli.base import sync
    ctx.invoke(sync)


@install.command('pkg', short_help='Install a package using system package manager')
@click.argument('pkg', required=True)
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@click.option('--target', '-t', required=False, help='Wildcard matching salt minions')
@default_options
@click.pass_context
def install_pkg(ctx, pkg, ssh, target):
    project = ctx.obj['project']
    args = [pkg]
    out = project.salt('pkg.install', args=args, target=target, ssh=ssh)
    click.echo(out)


@install.command('conda', short_help='Install conda package')
@click.argument('pkg', required=True)
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@click.option('--target', '-t', required=False, help='Wildcard matching salt minions')
@default_options
@click.pass_context
def install_conda(ctx, pkg, ssh, target):
    project = ctx.obj['project']
    out = project.salt('conda.install',
                       args=[pkg],
                       kwargs={'user': project.settings['USERNAME']},
                       target=target,
                       ssh=ssh)
    click.echo(out)


@install.command('notebook', short_help='Install Jupyter notebook in the head node')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@default_options
@click.pass_context
def install_notebook(ctx, ssh):
    project = ctx.obj['project']
    click.echo('Step 1/2: Conda (head only)')
    out = project.salt('state.sls', args=['miniconda'], target='head', ssh=ssh)
    click.echo(out)
    if not ssh:
        out = project.salt('saltutil.sync_all', target='head')
        click.echo(out)
    click.echo('Step 2/2: Jupyter Notebook')
    out = project.salt('state.sls', args=['ipython.notebook'], target='head', ssh=ssh)
    click.echo(out)


@install.command('hdfs', short_help='Install hdfs in the cluster')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@default_options
@click.pass_context
def install_hdfs(ctx, ssh):
    project = ctx.obj['project']
    click.echo('Step 1/1: HDFS')
    out = project.salt('state.sls', args=['cdh5.hdfs.cluster'], target='*', ssh=ssh)
    click.echo(out)


@install.command('mesos', short_help='Install mesos in the cluster')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@default_options
@click.pass_context
def install_mesos(ctx, ssh):
    project = ctx.obj['project']
    click.echo('Step 1/2: Zookeeper')
    out = project.salt('state.sls', args=['cdh5.zookeeper.cluster'], target='head', ssh=ssh)
    click.echo(out)
    click.echo('Step 2/2: Mesos')
    out = project.salt('state.sls', args=['mesos.cluster'], target='*', ssh=ssh)
    click.echo(out)


@install.command('marathon', short_help='Install mesos in the cluster')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@default_options
@click.pass_context
def install_marathon(ctx, ssh):
    project = ctx.obj['project']
    click.echo('Step 1/3: Zookeeper')
    out = project.salt('state.sls', args=['cdh5.zookeeper.cluster'], target='head', ssh=ssh)
    click.echo(out)
    click.echo('Step 2/3: Mesos')
    out = project.salt('state.sls', args=['mesos.cluster'], target='*', ssh=ssh)
    click.echo(out)
    click.echo('Step 3/3: Marathon')
    out = project.salt('state.sls', args=['mesos.marathon'], target='head', ssh=ssh)
    click.echo(out)


@install.command('spark', short_help='Install spark (on Mesos)')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@default_options
@click.pass_context
def install_spark(ctx, ssh):
    project = ctx.obj['project']
    click.echo('Step 1/4: Zookeeper')
    out = project.salt('state.sls', args=['cdh5.zookeeper.cluster'], target='head', ssh=ssh)
    click.echo(out)
    click.echo('Step 2/4: HDFS')
    out = project.salt('state.sls', args=['cdh5.hdfs.cluster'], target='*', ssh=ssh)
    click.echo(out)
    click.echo('Step 3/4: Mesos')
    out = project.salt('state.sls', args=['mesos.cluster'], target='*', ssh=ssh)
    click.echo(out)
    click.echo('Step 4/4: Spark on Mesos')
    out = project.salt('state.sls', args=['mesos.spark'], target='head', ssh=ssh)
    click.echo(out)


@install.command('impala', short_help='Install Impala')
@click.option('--ssh', is_flag=True, required=False, show_default=True, help='Whether to use ssh')
@default_options
@click.pass_context
def install_impala(ctx, ssh):
    project = ctx.obj['project']
    click.echo('Step 1/4: Zookeeper')
    out = project.salt('state.sls', args=['cdh5.zookeeper.cluster'], target='head', ssh=ssh)
    click.echo(out)
    click.echo('Step 2/4: HDFS')
    out = project.salt('state.sls', args=['cdh5.hdfs.cluster'], target='*', ssh=ssh)
    click.echo(out)
    click.echo('Step 3/4: Hive Metastore')
    out = project.salt('state.sls', args=['cdh5.hive.metastore'], target='head', ssh=ssh)
    click.echo(out)
    click.echo('Step 4/4: Impala')
    out = project.salt('state.sls', args=['cdh5.impala.cluster'], target='*', ssh=ssh)
    click.echo(out)
