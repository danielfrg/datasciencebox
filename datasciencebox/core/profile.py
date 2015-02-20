from __future__ import unicode_literals

import os
import copy

import yaml

from datasciencebox.core import config
from datasciencebox.core.cluster import Cluster
from datasciencebox.core.provider import load_providers


def load_profiles():
    profiles_files = [os.path.join(config.PROFILES_DIR, f) for f in os.listdir(config.PROFILES_DIR)
                       if f.endswith('.yaml') and
                       os.path.isfile(os.path.join(config.PROFILES_DIR, f))]

    profiles = Profiles()
    for file_ in profiles_files:
        p = BaseProfile.from_filepath(file_)
        profiles.append(p)
    return profiles


class Profiles(list):

    def get(self, name=None):
        if not name:
            return self[0]

        for item in self:
            if item.name == name:
                return item


class BaseProfile(object):

    def __init__(self, name):
        self.name = name
        self.provider = None
        self.attributes = {}

    def __repr__(self):
        return "Profile({0})".format(self.name)

    @classmethod
    def from_filepath(cls, filepath, providers=None):
        with open(filepath, 'r') as f:
            content = f.read()
        return BaseProfile.from_text(content, providers=providers)

    @classmethod
    def from_text(cls, text, providers=None):
        attrs = yaml.load(text)

        assert len(attrs) == 1, 'There should only be one root'
        root = attrs.keys()[0]

        assert 'provider' in attrs[root], 'Missing "provider" field in profile "%s"' % root
        provider_name = attrs[root]['provider']
        del attrs[root]['provider']
        providers = providers if providers else load_providers()
        provider = providers.get(provider_name)
        assert provider, 'Provider "%s" not found' % provider_name

        if provider.cloud == 'aws':
            profile_cls = AWSProfile

        profile = profile_cls(root)
        profile.provider = provider
        profile.fill_attrs(attrs[root])
        return profile

    def fill_attrs(self, attributes):
        for attr in attributes:
            self.attributes[attr] = attributes[attr]
            self.__setattr__(attr, attributes[attr])

    def __setattr__(self, name, value):
        super(BaseProfile, self).__setattr__(name, value)

    def validate(self):
        self.validate_fields()

    def validate_fields(self):
        for field in self.required_fields():
            assert field in self.attributes, 'Required field "%s" not in profile yaml file' % field
            assert getattr(self, field), 'Required field "%s" not in profile yaml file' % field

    def required_fields(self):
        raise NotImplementedError()

    def new_cluster(self, id='new'):
        cluster = Cluster(id, self)
        cluster.add_master()
        if 'minions' in self.attributes:
            n_minions = self.attributes['minions']['n']
            for i in range(n_minions):
                cluster.add_minion()
        return cluster


class AWSProfile(BaseProfile):

    def __repr__(self):
        return "AWSProfile({0})".format(self.name)

    def required_fields(self):
        return ['keypair', 'keyname', 'security_groups', 'image', 'size', 'user']


if __name__ == '__main__':
    profiles = load_profiles()
    print profiles

    p0 = profiles.get()
    c = p0.new_cluster('pew')
    print c
    print c.describe()
    # print c.create()
