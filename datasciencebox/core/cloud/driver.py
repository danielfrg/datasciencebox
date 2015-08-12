from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from datasciencebox.core.exceptions import DSBException, DSBWarning


class Driver(object):

    aws_region_map = {
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

    @classmethod
    def new(cls, dsbfile):
        cloud = dsbfile['CLOUD'].lower()
        if cloud == 'bare':
            return None
        elif cloud == 'aws':
            return Driver.aws_create(dsbfile)

    @classmethod
    def aws_create(cls, dsbfile):
        cls = get_driver(cls.aws_region_map[dsbfile['AWS_REGION'].lower()])
        return cls(dsbfile['AWS_KEY'], dsbfile['AWS_SECRET'])
