import pytest

from datasciencebox.core.settings import Settings
from datasciencebox.core.exceptions import DSBException


def test_required_bare_fields():
    settings = Settings()

    assert settings['CLOUD'] == 'bare'

    with pytest.raises(AssertionError) as excinfo:
        settings.validate_fields()

    settings['NODES'] = {}
    settings['USERNAME'] = 'root'
    settings['KEYPAIR'] = '~/.ssh/something'
    settings.validate_fields()


def test_required_aws_fields():
    settings = Settings()
    settings['CLOUD'] = 'aws'

    with pytest.raises(AssertionError) as excinfo:
        settings.validate_fields()

    settings['AWS_KEY'] = '1'
    settings['AWS_SECRET'] = '1'
    settings['AWS_KEYNAME'] = '1'
    settings['AWS_REGION'] = '1'
    settings['AWS_SECURITY_GROUPS'] = '1'
    settings['AWS_IMAGE'] = '1'
    settings['AWS_SIZE'] = '1'
    settings['USERNAME'] = '1'
    settings['KEYPAIR'] = '~/.ssh/something'
    settings['NUMBER_NODES'] = 3
    settings.validate_fields()
