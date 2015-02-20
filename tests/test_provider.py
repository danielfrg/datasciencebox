import pytest

from datasciencebox.core.provider import BaseProvider, AWSProvider
from datasciencebox.core.exception import ProviderError

provider_invalid = '''
fake:
  cloud: fake
'''

provider_aws = '''
aws:
  cloud: aws
  region: us-east-1
  key: XXXXXXXXXXXXXXXXXXXXXXXX
  secret: YYYYYYYYYYYYYYYYYYYYYYY
'''

provider_aws_invalid_1 = '''
aws_2:
  cloud: aws
  region: us-east-1
'''

def test_invalid():
    with pytest.raises(ProviderError) as excinfo:
        provider = BaseProvider.from_text(provider_invalid)


def test_aws():
    provider = BaseProvider.from_text(provider_aws)
    assert type(provider) == AWSProvider
    assert provider.cloud == 'aws'
    assert provider.name == 'aws'
    assert provider.region == 'us-east-1'
    assert provider.key == 'XXXXXXXXXXXXXXXXXXXXXXXX'
    assert provider.secret == 'YYYYYYYYYYYYYYYYYYYYYYY'
    assert provider.validate()

def test_aws_invalid_1():
    provider = BaseProvider.from_text(provider_aws_invalid_1)
    assert type(provider) == AWSProvider
    assert provider.name == 'aws_2'
    assert provider.cloud == 'aws'
    assert provider.region == 'us-east-1'
    with pytest.raises(AssertionError) as excinfo:
        assert provider.validate()
