import os
import importlib

from datasciencebox.core.exceptions import DSBException


class Settings(dict):

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self['CLOUD'] = 'bare'

    def validate_fields(self):
        for field in self.required_fields:
            assert field in self, 'Required field "%s" not found on dsbfile' % field
        return True

    @property
    def required_fields(self):
        if not 'CLOUD' in self:
            raise DSBException('"CLOUD" field missing')

        if self['CLOUD'] == 'bare':
            return ['NODES', 'USERNAME', 'KEYPAIR']
        elif self['CLOUD'] == 'aws':
            return ['NUMBER_NODES', 'AWS_KEY', 'AWS_SECRET', 'AWS_KEYNAME', 'AWS_SECURITY_GROUPS', 'AWS_IMAGE', 'AWS_SIZE', 'USERNAME', 'KEYPAIR']
        else:
            raise DSBException('Cloud "%s" not supported' % self['CLOUD'])

    @classmethod
    def from_dsbfile(cls, filepath):
        all_values = {}
        execfile(filepath, all_values)

        values = {}
        for setting in all_values:
            if setting.isupper():
                values[setting] = all_values[setting]
        return cls.from_dict(values)

    @classmethod
    def from_dict(cls, values):
        self = cls()
        self.update(values)
        self.validate_fields()
        return self


if __name__ == '__main__':
    dsbfile = Settings.from_dsbfile('../../dsbfile')
    print dsbfile
