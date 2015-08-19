from __future__ import absolute_import, unicode_literals

import webbrowser

import click

from datasciencebox.cli.main import main, log_option
from datasciencebox.core.project import Project


@main.group('open', short_help='Open an app UI/browser')
@log_option
@click.pass_context
def open_(ctx):
    ctx.obj = ctx.obj if ctx.obj else {}


@open_.command('mesos', short_help='Open the mesos UI')
@log_option
@click.pass_context
def open_mesos(ctx):
    project = Project.from_dir(path=ctx.obj['cwd'])
    url = 'http://%s:5050' % project.cluster.master.ip
    webbrowser.open(url, new=2)


@open_.command('mesos-marathon', short_help='Open the Marathon UI')
@log_option
@click.pass_context
def open_mesos_marathon(ctx):
    project = Project.from_dir(path=ctx.obj['cwd'])
    url = 'http://%s:8080' % project.cluster.master.ip
    webbrowser.open(url, new=2)


@open_.command('hdfs', short_help='Open the hdfs UI')
@log_option
@click.pass_context
def open_hdfs(ctx):
    project = Project.from_dir(path=ctx.obj['cwd'])
    url = 'http://%s:50070' % project.cluster.master.ip
    webbrowser.open(url, new=2)


@open_.command('notebook', short_help='Open the IPython notebook')
@log_option
@click.pass_context
def open_notebook(ctx):
    project = Project.from_dir(path=ctx.obj['cwd'])
    url = 'http://%s:8888' % project.cluster.master.ip
    webbrowser.open(url, new=2)
