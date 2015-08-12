import pytest

from datasciencebox.core.salt import generate_salt_cmd


def test_generate_salt_cmd():
    cmd = generate_salt_cmd('*', 'test.ping')
    assert cmd == ['"*"', 'test.ping']

    cmd = generate_salt_cmd('*', 'state.sls', args=['cdh5'])
    assert cmd == ['"*"', 'state.sls', 'cdh5']

    cmd = generate_salt_cmd('*', 'state.sls', args=['cdh5.something', 'arg2'])
    assert cmd == ['"*"', 'state.sls', 'cdh5.something', 'arg2']

    cmd = generate_salt_cmd('*', 'test.ping', kwargs={'user': 'root'})
    assert cmd == ['"*"', 'test.ping', 'user=root']

    cmd = generate_salt_cmd('*', 'test.ping', kwargs={'user': 'root', 'test': True})
    assert cmd == ['"*"', 'test.ping', 'test=True', 'user=root']

    cmd = generate_salt_cmd('*', 'conda.install', args=['a1', 'a2'], kwargs={'user': 'root', 'test': True})
    assert cmd == ['"*"', 'conda.install', 'a1', 'a2', 'test=True', 'user=root']
