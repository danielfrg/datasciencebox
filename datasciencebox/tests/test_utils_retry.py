import pytest

from datasciencebox.core.utils import retry


@retry(wait=0)
def dont_raise():
    return 35


@retry(wait=0)
def dont_raise_with_args(*args, **kwargs):
    return args, kwargs


@retry(wait=0)
def catch_Exception():
    raise Exception


@retry(wait=0, catch=(NotImplementedError, ))
def catch_NotImplementedException():
    raise NotImplementedError


@retry(wait=0, catch=(NotImplementedError, ))
def catch_NotImplementedException_raise_Exception():
    raise Exception


def test_retry_ok():
    assert dont_raise() == 35
    assert dont_raise_with_args('pew', 123, kw='args') == (('pew', 123), {'kw': 'args'})


def test_retry_raises_catch_ok():
    assert catch_Exception() == None
    assert catch_NotImplementedException() == None


def test_retry_raises_catch_fail():
    with pytest.raises(Exception):
        catch_NotImplementedException_raise_Exception()
