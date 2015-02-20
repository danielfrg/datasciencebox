import pytest

from datasciencebox.core.provider import Providers, BaseProvider
from datasciencebox.core.profile import BaseProfile

provider = '''
aws:
  cloud: aws
  region: us-east-1
'''

profile_invalid_no_provider = '''
small:
  not_provider: fake
'''

profile_invalid_provider = '''
small:
  provider: fake
'''

profile_aws_invalid = '''
small:
  provider: aws
  image: ami-eeb2ff86
  user: ubuntu
'''

profile_aws_valid_no_minions = '''
small:
  provider: aws
  size: m3.large
  image: ami-eeb2ff86
  user: ubuntu
  keyname: drodriguez
  keypair: ~/.ssh/my_aws.pem
  security_groups:
    - open
'''

profile_aws_valid_minions = '''
small:
  provider: aws
  size: m3.large
  image: ami-eeb2ff86
  user: ubuntu
  keyname: drodriguez
  keypair: ~/.ssh/my_aws.pem
  security_groups:
    - open
  minions:
    n: 11
    size: t1.micro
'''

def get_providers():
    providers = Providers()
    provider_ = BaseProvider.from_text(provider)
    providers.append(provider_)
    return providers

def test_profile_no_provider():
    with pytest.raises(AssertionError) as excinfo:
        BaseProfile.from_text(profile_invalid_no_provider, providers=get_providers())

def test_profile_invalid_provider():
    with pytest.raises(AssertionError) as excinfo:
        BaseProfile.from_text(profile_invalid_provider, providers=get_providers())

def test_profile_aws_invalid():
    profile = BaseProfile.from_text(profile_aws_invalid, providers=get_providers())
    assert profile.provider.name == get_providers()[0].name
    assert profile.user == 'ubuntu'
    assert profile.image == 'ami-eeb2ff86'
    with pytest.raises(AssertionError) as excinfo:
        profile.validate()

def test_profile_aws_valid_no_minions():
    profile = BaseProfile.from_text(profile_aws_valid_no_minions, providers=get_providers())
    assert profile.provider.name == get_providers()[0].name
    assert profile.user == 'ubuntu'
    assert profile.size == 'm3.large'
    assert profile.image == 'ami-eeb2ff86'
    assert profile.keyname == 'drodriguez'
    assert profile.keypair == '~/.ssh/my_aws.pem'
    assert profile.security_groups == ['open']
    profile.validate()
    with pytest.raises(AttributeError) as excinfo:
        profile.minions


def test_profile_aws_valid_minions():
    profile = BaseProfile.from_text(profile_aws_valid_minions, providers=get_providers())
    profile.validate()

    assert profile.minions['n'] == 11
    assert profile.minions['size'] == 't1.micro'
