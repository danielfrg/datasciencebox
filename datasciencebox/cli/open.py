from __future__ import absolute_import, unicode_literals

import webbrowser

import click

from datasciencebox.cli.main import main


@main.group('open', short_help='Open an app UI/browser')
@click.pass_context
def open_(ctx):
    ctx.obj = ctx.obj if ctx.obj else {}


@open_.command('mesos', short_help='Open the mesos UI')
@click.pass_context
def open_mesos(ctx):
    project = ctx.obj['project']
    url = 'http://%s:5050' % project.cluster.master.ip
    webbrowser.open(url, new=2)


@open_.command('hdfs', short_help='Open the hdfs UI')
@click.pass_context
def open_hdfs(ctx):
    project = ctx.obj['project']
    url = 'http://%s:50070' % project.cluster.master.ip
    webbrowser.open(url, new=2)


@open_.command('notebook', short_help='Open the IPython notebook')
@click.pass_context
def open_notebook(ctx):
    project = ctx.obj['project']
    url = 'http://%s:8888' % project.cluster.master.ip
    webbrowser.open(url, new=2)
