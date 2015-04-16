import os
import yaml

from datasciencebox.core.exceptions import DSBException


class DSBFile(dict):

    def __init__(self, *args, **kwargs):
        super(DSBFile, self).__init__(*args, **kwargs)
        self['cloud'] = 'bare'

    def validate_fields(self):
        for field in self.required_fields:
            assert field in self, 'Required field "%s" not found on dsbfile' % field
        return True

    @property
    def required_fields(self):
        if self['cloud'] == 'bare':
            return ['nodes', 'keypair', 'user']
        elif self['cloud'] == 'aws' or self['cloud'] == 'ec2':
            return ['key', 'secret', 'keypair', 'keyname', 'security_groups', 'image', 'size', 'user']
        else:
            raise DSBException('Cloud "%s" not supported' % self['cloud'])

    @classmethod
    def from_filepaths(cls, filepaths):
        data = {}
        for fpath in filepaths:
            with open(fpath, 'r') as f:
                dict_ = yaml.load(f.read())
                data.update(dict_)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, dict_):
        self = cls()
        self.update(dict_)
        return self
