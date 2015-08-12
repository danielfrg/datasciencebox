from __future__ import absolute_import, unicode_literals

import time

import click

from datasciencebox.cli.main import main
from datasciencebox.cli.utils import salt_ssh, salt_master


@main.group(short_help='Install packages, applications and more')
@click.pass_context
def install(ctx):
    ctx.obj = ctx.obj if ctx.obj else {}


@install.command(short_help='Install miniconda in the instances')
@click.argument('target', required=False)
@click.pass_context
def miniconda(ctx, target):
    project = ctx.obj['project']
    if not target:
        target = '*'
    salt_master(project, target, 'state.sls', 'miniconda')
    salt_master(project, target, 'saltutil.sync_all')


@install.command('salt', short_help='Install salt master and minion(s) via salt-ssh')
@click.pass_context
def salt(ctx):
    project = ctx.obj['project']

    pillar_template = """pillar='{"salt": {"master": {"ip": "%s"}, "minion": {"roles": %s } } }' """

    click.echo('Installing salt master in the head')
    salt_ssh(project, 'master', 'state.sls', 'salt.master')

    click.echo('Installing salt minion in the head')
    roles = """["java", "cdh5.hadoop.namenode", "cdh5.zookeeper", "cdh5.hive.metastore", "cdh5.impala.state-store"]"""
    roles = """["miniconda", "zookeeper", "mesos.master", "namenode", "ipython.notebook", "spark"]"""
    pillars = pillar_template % (project.cluster.master.ip, roles)
    salt_ssh(project, 'master', 'state.sls', 'salt.minion', pillars)

    # Minions
    click.echo('Installing salt minion in the compute')
    roles = """["java", "cdh5.hadoop.datanode", "cdh5.impala.server"]"""
    roles = """["miniconda", "mesos.slave", "datanode"]"""
    pillars = pillar_template % (project.cluster.master.ip, roles)
    salt_ssh(project, 'minion*', 'state.sls', 'salt.minion', pillars)


@install.command(short_help='Install a package using system package manager')
@click.pass_context
@click.argument('pkg', required=True)
@click.option('--target', '-t', required=False, help='Wildcard matching salt minions')
def pkg(ctx, pkg, target):
    project = ctx.obj['project']
    if not target:
        target = '*'
    salt_master(project, target, 'pkg.install', pkg)


@install.command(short_help='Install conda package')
@click.pass_context
@click.argument('pkg', required=True)
@click.option('--target', '-t', required=False, help='Wildcard matching salt minions')
def conda(ctx, pkg, target):
    project = ctx.obj['project']
    if not target:
        target = '*'
    salt_master(project, target, 'conda.install', pkg, user='dsb')


@install.command(short_help='Install ipython notebook in the master')
@click.pass_context
def notebook(ctx):
    project = ctx.obj['project']
    salt_master(project, 'master', 'state.sls', 'ipython.notebook')


@install.command(short_help='Install hdfs in the cluster')
@click.pass_context
def hdfs(ctx):
    project = ctx.obj['project']
    salt_master(project, 'master', 'state.sls', 'cdh5.hdfs.namenode')
    salt_master(project, 'minion*', 'state.sls', 'cdh5.hdfs.datanode')


@install.command(short_help='Install mesos in the cluster')
@click.pass_context
def mesos(ctx):
    project = ctx.obj['project']
    salt_master(project, 'master', 'state.sls', 'cdh5.zookeeper')
    salt_master(project, 'master', 'state.sls', 'mesos.master')
    salt_master(project, 'minion*', 'state.sls', 'mesos.slave')


@install.command(short_help='Install spark in the master')
@click.pass_context
def spark(ctx):
    project = ctx.obj['project']
    salt_master(project, 'master', 'state.sls', 'mesos.spark')
