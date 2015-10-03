import pytest

from datasciencebox.core.settings import Settings
from datasciencebox.core.cloud.instance import Instance, BareInstance, AWSInstance, GCPInstance

default_username = 'default_username'
default_keypair = 'default_keypair'

settings = Settings()
settings['USERNAME'] = default_username
settings['KEYPAIR'] = default_keypair


def test_new_bare():
    instance = Instance.new(settings=settings)
    assert isinstance(instance, BareInstance)

    instance = Instance.new(settings=settings, uid='myid')
    assert instance.uid == 'myid'
    assert instance.port == 22
    assert instance.username == default_username
    assert instance.keypair == default_keypair

    instance = Instance.new(settings=settings,
                            uid='myid',
                            ip='1.1.1.1',
                            port=33,
                            username='me',
                            keypair='mykey')
    assert instance.ip == '1.1.1.1'
    assert instance.port == 33
    assert instance.username == 'me'
    assert instance.keypair == 'mykey'
    assert instance.to_dict() == {'ip': '1.1.1.1', 'port': 33, 'uid': 'myid'}


def test_new_bare_ip_with_port():
    instance = Instance.new(settings=settings, uid='myid', ip='1.1.1.1:2022')
    assert isinstance(instance, BareInstance)
    assert instance.ip == '1.1.1.1'
    assert instance.port == 2022
    assert instance.username == default_username
    assert instance.keypair == default_keypair


def test_new_clouds():
    settings['CLOUD'] = 'aws'
    instance = Instance.new(settings=settings)
    assert isinstance(instance, AWSInstance)

    settings['CLOUD'] = 'gcp'
    instance = Instance.new(settings=settings)
    assert isinstance(instance, GCPInstance)
