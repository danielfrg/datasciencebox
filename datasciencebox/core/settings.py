from datasciencebox.core.logger import getLogger
logger = getLogger()
from datasciencebox.core.exceptions import DSBException


class Settings(dict):

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        logger.debug('Initializing Settings')
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
            return ['NUMBER_NODES', 'AWS_KEY', 'AWS_SECRET', 'AWS_KEYNAME', 'AWS_REGION',
                    'AWS_SECURITY_GROUPS', 'AWS_IMAGE', 'AWS_SIZE', 'USERNAME', 'KEYPAIR']
        elif self['CLOUD'] == 'gcp':
            return ['NUMBER_NODES', 'GCP_EMAIL', 'GCP_KEY_FILE', 'GCP_PROJECT', 'GCP_DATACENTER',
                    'GCP_IMAGE', 'GCP_SIZE', 'GCP_PUBLIC_KEY', 'GCP_NETWORK', 'USERNAME', 'KEYPAIR']
        else:
            raise DSBException('Cloud "%s" not supported' % self['CLOUD'])

    @classmethod
    def from_dsbfile(cls, filepath):
        logger.debug('Creating settings from: %s', filepath)
        all_values = {}
        execfile(filepath, all_values)

        values = {}
        for setting in all_values:
            if setting.isupper():
                values[setting] = all_values[setting]
        return cls.from_dict(values)

    @classmethod
    def from_dict(cls, values):
        logger.debug('Creating settings from dictionary')
        self = cls()
        self.update(values)
        self.validate_fields()
        return self


if __name__ == '__main__':
    dsbfile = Settings.from_dsbfile('../../dsbfile')
    print dsbfile
