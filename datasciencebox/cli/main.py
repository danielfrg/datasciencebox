from __future__ import absolute_import

import os
import sys
import logging
import traceback
from functools import update_wrapper

import click

from datasciencebox.core.project import Project
from datasciencebox.core.exceptions import DSBException

from datasciencebox.core.logger import setup_logging


def start():
    try:
        cli(obj={})
    except DSBException as e:
        click.echo('ERROR: %s' % e, err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo(
            "Interrupted by Ctrl-C. One or more actions could be still running in the cluster")
        sys.exit(1)
    except Exception as e:
        click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


def default_options(func):

    @click.option('--file',
                  '-f',
                  'settingsfile',
                  required=False,
                  help='Path to the file to use as dsbfile',
                  type=click.Path(exists=True,
                                  resolve_path=True))
    @click.option('--log-level',
                  '-l',
                  required=False,
                  default='warning',
                  type=click.Choice(['debug', 'warning', 'error']),
                  show_default=True,
                  help='Logging level')
    @click.pass_context
    def new_func(ctx, settingsfile, log_level, *args, **kwargs):
        if 'log_level' not in ctx.obj:
            if log_level == 'info':
                log_level = logging.INFO
            elif log_level == 'debug':
                log_level = logging.DEBUG
            elif log_level == 'warning':
                log_level = logging.WARNING
            elif log_level == 'error':
                log_level = logging.ERROR
            setup_logging(log_level)
            ctx.obj['log_level'] = log_level

        if 'project' not in ctx.obj:
            if settingsfile:
                project = Project.from_file(settingsfile)
            else:
                project = Project.from_dir(path=ctx.obj['cwd'])
            ctx.obj['project'] = project

        return ctx.invoke(func, *args, **kwargs)

    return update_wrapper(new_func, func)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    ctx.obj = {}
    ctx.obj['cwd'] = os.getcwd()


from datasciencebox.cli.base import *
from datasciencebox.cli.open import *
from datasciencebox.cli.install import *

if __name__ == '__main__':
    start()
