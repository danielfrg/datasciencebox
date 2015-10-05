import pytest

import os
import sys
import json

from click.testing import CliRunner

from ...cli.main import cli
from ...core.project import Project

vagranttest = pytest.mark.skipif('TEST_DSBFILE' not in os.environ,
                                 reason="Environment variable 'TEST_DSBFILE' is required")


def get_test_project():
    dsbfile = os.environ['TEST_DSBFILE']
    return Project.from_file(dsbfile)


def invoke(*args):
    dsbfile = os.environ['TEST_DSBFILE']
    args = list(args)
    args.extend(['--file', dsbfile])
    runner = CliRunner()
    return runner.invoke(cli, args, catch_exceptions=False, input=sys.stdin)


def check_all_true(salt_output, none_is_ok=False):
    minions = []
    for minion_output in salt_output.split('\n'):
        minions.append(json.loads(minion_output))

    for minion in minions:
        minion_values = minion.values()[0]
        for id_, value in minion_values.items():
            if none_is_ok:
                assert value['result'] is not False, (id_, value)
            else:
                assert value['result'] is True, (id_, value)


def check_all_cmd_retcode0(salt_output):
    minions = []
    for minion_output in salt_output.split('\n'):
        minions.append(json.loads(minion_output))

    for minion in minions:
        minion_output = minion.values()[0]
        assert minion_output['retcode'] == 0, (minion_output)
