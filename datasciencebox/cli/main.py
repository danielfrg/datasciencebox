from __future__ import absolute_import, unicode_literals

import os
import sys
import logging
import traceback
from functools import update_wrapper

import click

from datasciencebox.core.exceptions import DSBException

from datasciencebox.core.logger import setup_logging


def start():
    try:
        main(obj={})
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


def log_option(func):

    @click.option('--log-level', '-l',
                  required=False,
                  default='error',
                  type=click.Choice(['debug', 'error']),
                  show_default=True,
                  help='Logging level')
    @click.pass_context
    def new_func(ctx, log_level, *args, **kwargs):
        if log_level == 'info':
            log_level = logging.INFO
        elif log_level == 'debug':
            log_level = logging.DEBUG
        elif log_level == 'error':
            log_level = logging.ERROR
        setup_logging(log_level)

        ctx.obj['log_level'] = log_level
        return ctx.invoke(func, *args, **kwargs)

    return update_wrapper(new_func, func)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def main(ctx):
    ctx.obj = {}
    ctx.obj['cwd'] = os.getcwd()


from datasciencebox.cli.base import *
from datasciencebox.cli.open import *
from datasciencebox.cli.install import *

if __name__ == '__main__':
    start()
