from __future__ import unicode_literals

import os
import copy

import yaml
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from datasciencebox.core import config


def load_providers():
    providers_files = [os.path.join(config.PROVIDERS_DIR, f) for f in os.listdir(config.PROVIDERS_DIR)
                       if f.endswith('.yaml') and
                       os.path.isfile(os.path.join(config.PROVIDERS_DIR, f))]

    providers = Providers()
    for file_ in providers_files:
        p = BaseProvider.from_filepath(file_)
        providers.append(p)
    return providers


class Providers(list):

    def get(self, name=None):
        if not name:
            return self[0]

        for item in self:
            if item.name == name:
                return item


class BaseProvider(object):

    def __init__(self, name):
        self.name = name
        self.cloud = None
        self._driver = None
        self.attributes = {}

    def get_driver(self):
        if not self._driver:
            self._driver = self.create_driver()
        return self._driver

    def set_driver(self, value):
        self._driver = value

    driver = property(get_driver, set_driver, None, "apache-libcloud driver")

    def __repr__(self):
        return 'Provider({0})'.format(self.name)

    @classmethod
    def from_filepath(cls, filepath):
        with open(filepath, 'r') as f:
            attrs = yaml.load(f)

            assert len(attrs) == 1, 'There should only be one root in the provider yaml file'
            root = attrs.keys()[0]

            assert 'cloud' in attrs[root], '"cloud" field not found in provider yaml'
            cloud = attrs[root]['cloud']
            del attrs[root]['cloud']

            if cloud == 'aws':
                cls = AWSProvider
            else:
                Exception('Cloud(%s) not yet supported' % cloud)

        provider = cls(root)
        provider.fill_attrs(attrs[root])
        provider.validate()
        return provider

    def fill_attrs(self, attributes):
        for attr in attributes:
            self.attributes[attr] = attributes[attr]
            self.__setattr__(attr, attributes[attr])

    def __setattr__(self, name, value):
        super(BaseProvider, self).__setattr__(name, value)

    def validate(self):
        self.validate_fields()

    def validate_fields(self):
        for field in self.required_fields():
            assert field in self.attributes, 'Required field "%s" not in provider yaml file' % field
            assert getattr(self, field), 'Required field "%s" not in provider  yaml file' % field

    def required_fields(self):
        raise NotImplementedError()

    def create_driver(self):
        raise NotImplementedError()


class AWSProvider(BaseProvider):

    region_map = {
        'us-east-1': Provider.EC2_US_EAST,
        'us-west-1': Provider.EC2_US_WEST,
        'us-west-2': Provider.EC2_US_WEST_OREGON,
        'eu-west-1': Provider.EC2_EU_WEST,
        'eu-central-1': None,
        'sa-east-1': Provider.EC2_SA_EAST,
        'ap-northeast-1': Provider.EC2_AP_NORTHEAST,
        'ap-southeast-1': Provider.EC2_AP_SOUTHEAST,
        'ap-southeast-2': Provider.EC2_AP_SOUTHEAST2,
    }

    def __init__(self, *args, **kwargs):
        super(AWSProvider, self).__init__(*args, **kwargs)
        self.cloud = 'aws'

    def __repr__(self):
        return 'AWSProvider({0})'.format(self.name)

    def required_fields(self):
        return ['region', 'key', 'secret']

    def create_driver(self):
        cls = get_driver(self.region_map[self.region.lower()])
        return cls(self.key, self.secret)


if __name__ == '__main__':
    providers = load_providers()
    print providers

    p0 = providers.get()
    print p0.get_driver()

