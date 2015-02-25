from __future__ import unicode_literals

import os
import shutil
import subprocess
import webbrowser

import click
from fabric.api import settings, run, sudo

from datasciencebox.cli import rsync as rsync_
from datasciencebox.core import config
from datasciencebox.core import profile as profile_module
from datasciencebox.core import provider as provider_module
from datasciencebox.core import cluster as cluster_module


def get_cluster(cluster_name=None):
    clusters = cluster_module.load_clusters()
    if cluster_name:
        return clusters.get(cluster_name)
    else:
        if len(clusters) == 0:
            raise Exception('No clusters found')
        return clusters[0]


def salt_master_call(cluster, target, module, args=None, args2=None, user=None):
    host_string = cluster.master.profile.user + '@' + cluster.master.ip
    key_filename = cluster.master.profile.keypair
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


def salt_ssh_call(cluster, target, module, args=None, args2=None):
    roster_file = '--roster-file=%s' % cluster.get_roster_path()
    config_dir = '--config-dir=%s' % cluster.get_salt_config_dir()
    cmd = ['salt-ssh', roster_file, config_dir, '--ignore-host-keys', target, module]
    if args:
        cmd = cmd + [args]
    if args2:
        cmd = cmd + [args2]

    cmd = cmd + ['--state-output=mixed']
    cmd = ' '.join(cmd)
    print cmd
    subprocess.call(cmd, shell=True)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


@main.command(short_help='Create instance(s) based on a profile')
@click.argument('cluster-name')
@click.option('--profile', '-p', required=False, default=None, help='Profile name')
def create(cluster_name, profile):
    profile = profile_module.load_profiles().get(profile)
    profile.validate()
    cluster = profile.new_cluster(cluster_name)
    cluster.create()
    cluster.save_info()
    cluster.save_roster()
    cluster.create_salt_ssh_files()


@main.command(short_help='Describe a cluster')
@click.argument('cluster-name', required=False)
def describe(cluster_name):
    cluster = get_cluster(cluster_name)

    print 'Master: ', cluster.master.ip
    if cluster.minions:
        print 'Minions(x%s): ' % len(cluster.minions)
        for minion in cluster.minions:
            print '  -', '%s:' % minion.name, minion.ip


@main.command('describe-new', short_help='Describe a new cluster that would be created')
@click.argument('profile')
def describe_new(profile):
    profile = profile_module.load_profiles().get(profile)
    profile.validate()
    print profile.new_cluster('new').describe()


@main.command(short_help='Destroy a cluster')
@click.argument('cluster-name', required=False)
def destroy(cluster_name):
    cluster = get_cluster(cluster_name)
    cluster.destroy()
    shutil.rmtree(os.path.join(config.CLUSTERS_DIR, cluster.name))

# --------------------------------------------------------------------------------------------------
# INSTALL
# --------------------------------------------------------------------------------------------------

@main.group(short_help='Install application')
@click.option('--cluster-name', '-c', required=False, help='Cluster name')
@click.pass_context
def install(ctx, cluster_name):
    ctx.obj = {}
    ctx.obj['cluster'] = get_cluster(cluster_name)


@install.command(short_help='Install conda package')
@click.pass_context
@click.argument('pkg', required=True)
@click.argument('target', required=False)
def conda(ctx, pkg, target):
    cluster = ctx.obj['cluster']
    if not target:
        target = '*'
    salt_master_call(cluster, target, 'conda.install', pkg, user='dsb')


@install.command(short_help='Install a package using system package manager')
@click.pass_context
@click.argument('pkg', required=True)
@click.argument('target', required=False)
def pkg(ctx, pkg, target):
    cluster = ctx.obj['cluster']
    if not target:
        target = '*'
    salt_master_call(cluster, target, 'pkg.install', pkg)


@install.command(short_help='Install a pypi package')
@click.pass_context
@click.argument('pkg', required=True)
@click.argument('target', required=False)
def pip(ctx, pkg, target):
    cluster = ctx.obj['cluster']
    if not target:
        target = '*'
    salt_master_call(cluster, target, 'conda.install', pkg, user='dsb')


@install.command(short_help='Install hdfs in the cluster')
@click.pass_context
def hdfs(ctx):
    cluster = ctx.obj['cluster']
    salt_master_call(cluster, cluster.master.name, 'state.sls', 'cdh5.hdfs.namenode')
    salt_master_call(cluster, '*minion*', 'state.sls', 'cdh5.hdfs.datanode')


@install.command(short_help='Install mesos in the cluster')
@click.pass_context
def mesos(ctx):
    cluster = ctx.obj['cluster']
    salt_master_call(cluster, cluster.master.name, 'state.sls', 'mesos.master')
    salt_master_call(cluster, '*minion*', 'state.sls', 'mesos.slave')


@install.command(short_help='Install miniconda in the instances')
@click.argument('target', required=False)
@click.pass_context
def miniconda(ctx, target):
    cluster = ctx.obj['cluster']
    if not target:
        target = '*'
    salt_master_call(cluster, target, 'state.sls', 'miniconda')
    salt_master_call(cluster, target, 'saltutil.sync_all')


@install.command('salt', short_help='Install salt master and minion(s) via salt-ssh')
@click.pass_context
def install_salt(ctx):
    cluster = ctx.obj['cluster']
    pillar_template = '''pillar='{"salt": {"master": {"ip": "%s"}, "minion": {"roles": %s } } }' '''

    # Master
    salt_ssh_call(cluster, cluster.master.name, 'state.sls', 'salt.master')
    roles = '''["miniconda", "zookeeper", "mesos.master", "namenode", "ipython.notebook", "spark"]'''
    roles = '''["java", "cdh5.hadoop.namenode", "cdh5.zookeeper", "cdh5.hive.metastore", "cdh5.impala.state-store"]'''
    pillars = pillar_template % (cluster.master.ip, roles)
    salt_ssh_call(cluster, cluster.master.name, 'state.sls', 'salt.minion', pillars)

    # Minions
    roles = '''["miniconda", "mesos.slave", "datanode"]'''
    roles = '''["java", "cdh5.hadoop.datanode", "cdh5.impala.server"]'''
    pillars = pillar_template % (cluster.master.ip, roles)
    salt_ssh_call(cluster, '*minion*', 'state.sls', 'salt.minion', pillars)

    salt_master_call(cluster, '*', 'saltutil.sync_all')


@install.command(short_help='Install spark in the master')
@click.pass_context
def spark(ctx):
    cluster = ctx.obj['cluster']
    salt_master_call(cluster, cluster.master.name, 'state.sls', 'spark')
    salt_master_call(cluster, cluster.master.name, 'state.sls', 'mesos.spark')


@install.command(short_help='Install ipython notebook in the master')
@click.pass_context
def notebook(ctx):
    cluster = ctx.obj['cluster']
    salt_master_call(cluster, cluster.master.name, 'state.sls', 'ipython.notebook')

# --------------------------------------------------------------------------------------------------

@main.command('list', short_help='List all running clusters')
def list():
    clusters = cluster_module.load_clusters()
    for i, cluster in enumerate(clusters):
        if i == 0:
            print cluster.name + ' (default)'
        else:
            print cluster.name

# --------------------------------------------------------------------------------------------------
# OPEN
# --------------------------------------------------------------------------------------------------

@main.group('open', short_help='Open an app UI/browser/etc')
@click.option('--cluster-name', '-c', required=False, help='Cluster name')
@click.pass_context
def open_(ctx, cluster_name):
    ctx.obj = {}
    ctx.obj['cluster'] = get_cluster(cluster_name)


@open_.command('mesos', short_help='Open the mesos UI')
@click.pass_context
def open_mesos(ctx):
    cluster = ctx.obj['cluster']
    url = 'http://%s:5050' % cluster.master.ip
    webbrowser.open(url, new=2)


@open_.command('hdfs', short_help='Open the hdfs UI')
@click.pass_context
def open_hdfs(ctx):
    cluster = ctx.obj['cluster']
    url = 'http://%s:50070' % cluster.master.ip
    webbrowser.open(url, new=2)


@open_.command('notebook', short_help='Open the IPython notebook')
@click.pass_context
def open_notebook(ctx):
    cluster = ctx.obj['cluster']
    url = 'http://%s:8888' % cluster.master.ip
    webbrowser.open(url, new=2)

# --------------------------------------------------------------------------------------------------

@main.command(short_help='Advanced: rsync salt states to master')
@click.argument('cluster-name', required=False)
@click.option('--once', '-o', required=False,  is_flag=True, help='Only sync once, not continuosly')
def rsync(cluster_name, once):
    cluster = get_cluster(cluster_name)
    handler = rsync_.RsyncHandler()
    handler.cluster = cluster
    handler.sync_all()
    if not once:
        print 'Initial rsync done'
        rsync_.loop(cluster, handler)


@main.command(short_help='Execute commands using the salt-master')
@click.argument('target', required=True)
@click.argument('module', required=True)
@click.argument('args', required=False)
@click.argument('args2', required=False)
@click.option('--cluster-name', '-c', required=False, help='Cluster name')
def salt(target, module, args, args2, cluster_name):
    cluster = get_cluster(cluster_name)
    salt_master_call(cluster, target, module, args, args2)


@main.command(short_help='Run salt state.highstate')
@click.option('--cluster-name', '-c', required=False, help='Cluster name')
@click.argument('target', required=False)
def highstate(target, cluster_name):
    cluster = get_cluster(cluster_name)
    target = target if target else '*'
    salt_master_call(cluster, target, 'state.highstate')


@main.command('salt-ssh', short_help='Execute commands using salt-ssh')
@click.argument('target', required=True)
@click.argument('module', required=True)
@click.argument('args', required=False)
@click.argument('args2', required=False)
@click.option('--cluster-name', '-c', required=False, help='Cluster name')
def salt_ssh(target, module, args, args2, cluster_name):
    cluster = get_cluster(cluster_name)
    salt_ssh_call(cluster, target, module, args, args2)


@main.command(short_help='SSH to the master of the cluster')
@click.argument('cluster-name', required=False)
def ssh(cluster_name):
    cluster = get_cluster(cluster_name)
    cmd = ['ssh', cluster.master.profile.user + '@' + cluster.master.ip]
    cmd = cmd + ['-i', os.path.expanduser(cluster.master.profile.keypair)]
    cmd = cmd + ['-oStrictHostKeyChecking=no']
    subprocess.call(cmd)


@main.command('update-config', short_help='Update cluster config')
@click.argument('cluster-name', required=False)
def update_config(cluster_name):
    cluster = get_cluster(cluster_name)
    cluster.update_config()


if __name__ == '__main__':
    main()
