import pytest

from datasciencebox.core.settings import Settings
from datasciencebox.core.cloud.instance import Instance, BareInstance, AWSInstance, GCPInstance

settings = Settings()


def test_new_bare():
    instance = Instance.new(settings=settings)
    assert isinstance(instance, BareInstance)

    instance = Instance.new(settings=settings, uid='myid')
    assert instance.uid == 'myid'

    instance = Instance.new(settings=settings, uid='myid', ip='1.1.1.1')
    assert instance.ip == '1.1.1.1'


def test_new_others():
    settings['CLOUD'] = 'aws'
    instance = Instance.new(settings=settings)
    assert isinstance(instance, AWSInstance)


    settings['CLOUD'] = 'gcp'
    instance = Instance.new(settings=settings)
    assert isinstance(instance, GCPInstance)
