from __future__ import absolute_import, unicode_literals

import webbrowser

import click

from datasciencebox.cli.main import cli, default_options


@cli.group('open', short_help='Open an app UI/browser')
@click.pass_context
def open_(ctx):
    pass


@open_.command('mesos', short_help='Open the mesos UI')
@default_options
@click.pass_context
def open_mesos(ctx):
    project = ctx.obj['project']
    url = 'http://%s:5050' % project.cluster.head.ip
    webbrowser.open(url, new=2)


@open_.command('marathon', short_help='Open the Marathon UI')
@default_options
@click.pass_context
def open_marathon(ctx):
    project = ctx.obj['project']
    url = 'http://%s:8080' % project.cluster.head.ip
    webbrowser.open(url, new=2)


@open_.command('hdfs', short_help='Open the hdfs UI')
@default_options
@click.pass_context
def open_hdfs(ctx):
    project = ctx.obj['project']
    url = 'http://%s:50070' % project.cluster.head.ip
    webbrowser.open(url, new=2)


@open_.command('notebook', short_help='Open the IPython notebook')
@default_options
@click.pass_context
def open_notebook(ctx):
    project = ctx.obj['project']
    url = 'http://%s:8888' % project.cluster.head.ip
    webbrowser.open(url, new=2)
