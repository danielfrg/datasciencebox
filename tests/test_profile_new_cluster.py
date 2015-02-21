import pytest

from datasciencebox.core.provider import Providers, BaseProvider
from datasciencebox.core.profile import BaseProfile
from datasciencebox.core.cluster import AWSInstance

provider = '''
aws:
  cloud: aws
  region: us-east-1
'''

profile_aws = '''
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
    n: 4
    size: t1.micro
    image: ami-aa22ff33
'''

def get_providers():
    providers = Providers()
    provider_ = BaseProvider.from_text(provider)
    providers.append(provider_)
    return providers

def test_profile_aws_valid_minions_1():
    profile = BaseProfile.from_text(profile_aws, providers=get_providers())
    profile.validate()

    cluster = profile.new_cluster('new-cluster')
    assert type(cluster.master) == AWSInstance
    assert cluster.master.name == 'new-cluster-master'
    assert cluster.master.profile.size == 'm3.large'
    assert cluster.master.profile.image == 'ami-eeb2ff86'
    assert cluster.master.profile.user == 'ubuntu'
    assert cluster.master.profile.keyname == 'drodriguez'
    assert cluster.master.profile.keypair == '~/.ssh/my_aws.pem'

    assert len(cluster.minions) == 4
    for i, minion in enumerate(cluster.minions):
      assert type(minion) == AWSInstance
      assert minion.name == 'new-cluster-minion-%i' % (i + 1)
      assert minion.profile.size == 't1.micro'
      assert minion.profile.image == 'ami-aa22ff33'
      assert minion.profile.user == 'ubuntu'
      assert minion.profile.keyname == 'drodriguez'
      assert minion.profile.keypair == '~/.ssh/my_aws.pem'
