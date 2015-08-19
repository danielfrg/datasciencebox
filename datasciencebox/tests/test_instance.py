import pytest

from datasciencebox.core.settings import Settings
from datasciencebox.core.cloud.instance import Instance, BareInstance, AWSInstance

settings = Settings()


def test_bare_new():
    instance = Instance.new(settings=settings)
    assert type(instance) == BareInstance


def test_bare_fromdict_todict():
    instance = Instance.from_uid('fakeid', settings=settings)
    assert instance.uid == 'fakeid'
