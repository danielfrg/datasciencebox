import pytest

import os
import sys
import json

from click.testing import CliRunner

from ...cli.main import cli
from ...core.project import Project

vagranttest = pytest.mark.skipif('VAGRANT_DSBFILE' not in os.environ,
                                 reason="Environment variable 'VAGRANT_DSBFILE' is required")


def get_test_project():
    dsbfile = os.environ['VAGRANT_DSBFILE']
    return Project.from_file(dsbfile)


def invoke(*args):
    dsbfile = os.environ['VAGRANT_DSBFILE']
    args = list(args)
    args.extend(['--file', dsbfile])
    runner = CliRunner()
    return runner.invoke(cli, args, catch_exceptions=False, input=sys.stdin)


def check_all_true(salt_output):
    out = []
    for minion_output in salt_output.split('\n'):
        out.append(json.loads(minion_output))

    for minion in out:
        minion_values = minion.values()[0]
        for id_, value in minion_values.items():
            assert value['result'] == True, (id_, value)
