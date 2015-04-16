import pytest

from datasciencebox.core.dsbfile import DSBFile
from datasciencebox.core.exceptions import DSBException


def test_required_bare_fields():
    dsbfile = DSBFile()

    assert dsbfile['cloud'] == 'bare'

    with pytest.raises(AssertionError) as excinfo:
        dsbfile.validate_fields()

    dsbfile['nodes'] = {}
    dsbfile['user'] = 'root'
    dsbfile['keypair'] = '~/.ssh/something'
    dsbfile.validate_fields()


def test_required_aws_fields():
    dsbfile = DSBFile()
    dsbfile['cloud'] = 'aws'

    with pytest.raises(AssertionError) as excinfo:
        dsbfile.validate_fields()

    dsbfile['key'] = '1'
    dsbfile['secret'] = '1'
    dsbfile['keypair'] = '1'
    dsbfile['keyname'] = '1'
    dsbfile['security_groups'] = '1'
    dsbfile['image'] = '1'
    dsbfile['size'] = '1'
    dsbfile['user'] = '1'
    dsbfile.validate_fields()
