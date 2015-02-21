import pytest

from datasciencebox.core.provider import Providers, BaseProvider
from datasciencebox.core.profile import Profiles, BaseProfile
from datasciencebox.core.cluster import Cluster, AWSInstance

provider = '''
aws:
  cloud: aws
  region: us-east-1
'''

profile = '''
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
    n: 2
    size: t1.micro
'''

cluster_aws_valid = '''
temp:
  master:
    id: i-111
    ip: 1.1.1.111
    name: temp-master
    private_dns: ip-1-1-1-111.ec2.internal
  minions:
  - temp-minion-1:
      id: i-222
      ip: 2.2.2.222
      private_dns: ip-2-2-2-222.ec2.internal
  - temp-minion-2:
      id: i-333
      ip: 3.3.3.333
      private_dns: ip-3-3-3-333.ec2.internal
  profile: small
'''

def get_providers():
    providers = Providers()
    provider_ = BaseProvider.from_text(provider)
    providers.append(provider_)
    return providers

def get_profiles():
    profiles = Profiles()
    profile_ = BaseProfile.from_text(profile, providers=get_providers())
    profiles.append(profile_)
    return profiles

def test_aws_valid():
    profiles = get_profiles()
    cluster = Cluster.from_text(cluster_aws_valid, profiles=profiles)

    assert type(cluster.master) == AWSInstance
    assert cluster.master.id == 'i-111'
    assert cluster.master.name == 'temp-master'
    assert cluster.master.ip == '1.1.1.111'
    assert cluster.master.private_dns == 'ip-1-1-1-111.ec2.internal'

    assert len(cluster.minions) == 2
    minion_1 = cluster.minions[0]
    assert type(minion_1) == AWSInstance
    assert minion_1.id == 'i-222'
    assert minion_1.name == 'temp-minion-1'
    assert minion_1.ip == '2.2.2.222'
    assert minion_1.private_dns == 'ip-2-2-2-222.ec2.internal'

    minion_2 = cluster.minions[1]
    assert type(minion_2) == AWSInstance
    assert minion_2.id == 'i-333'
    assert minion_2.name == 'temp-minion-2'
    assert minion_2.ip == '3.3.3.333'
    assert minion_2.private_dns == 'ip-3-3-3-333.ec2.internal'

def test_aws_valid_roster():
    profiles = get_profiles()
    cluster = Cluster.from_text(cluster_aws_valid, profiles=profiles)

    roster = cluster.generate_roster()
    assert len(roster)
