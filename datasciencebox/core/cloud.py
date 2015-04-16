import os
import yaml
import warnings

from libcloud.compute.base import NodeImage
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from datasciencebox.core.exceptions import DSBException, DSBWarning


class Cluster(object):

    def __init__(self):
        self._driver = None
        self.dsbfile = None
        self.instances = []

    @classmethod
    def from_filepath(cls, filepath, info):
        with open(filepath, 'r') as f:
            list_ = yaml.load(f.read())
            return cls.from_list(list_, info)

    @classmethod
    def from_list(cls, list_, info):
        '''
        From a list of dicts, how
        '''
        self = cls()
        self.dsbfile = info
        self.instances = []

        for instance in list_:
            new_instance = Instance.new(self.dsbfile, info=instance)
            self.instances.append(new_instance)

        return self

    def to_list(self):
        '''
        To a list of dicts
        '''
        ret = []
        for instance in self.instances:
            ret.append(instance.to_dict())
        return ret

    @property
    def master(self):
        return self.instances[0]

    @property
    def driver(self):
        if self._driver is None:
            self._driver = Driver.new(self.dsbfile)
        return self._driver

    def create(self):
        if self.dsbfile['cloud'] == 'bare':
            warnings.warn("Bare Metal cluster cannot be created", DSBWarning)
            return

        instances = []

        master_ins = Instance.new(dsbfile=self.dsbfile, driver=self.driver)
        instances.append(master_ins)

        if 'minion' in self.dsbfile and 'number' in self.dsbfile['minion']:
            number = self.dsbfile['minion']['number']
            for i in range(number):
                n_ins = Instance.new(dsbfile=self.dsbfile, driver=self.driver)
                instances.append(n_ins)

        _ = [instance.create() for instance in instances]
        nodes = [instance.node for instance in instances]
        self.driver.wait_until_running(nodes)

        new_nodes = self.driver.list_nodes(ex_node_ids=[node.id for node in nodes])
        for instance, node in zip(instances, new_nodes):
            instance.node = node
        self.instances = instances

    def fetch_nodes(self):
        for instance in self.instances:
            instance.driver = self.driver
            instance.fetch_node()

    def destroy(self):
        for instance in self.instances:
            instance.destroy()


class Instance(object):

    def __init__(self, data, driver=None):
        self.data = data
        self.driver = driver
        self._node = None

        self._id = None
        self._ip = None

    @classmethod
    def new(cls, dsbfile=None, driver=None, info=None):
        cloud = dsbfile['cloud']
        if cloud == 'bare':
            self = BareInstance(dsbfile, driver=driver)
        elif cloud == 'aws':
            self = AWSInstance(dsbfile, driver=driver)
        else:
            raise DSBException('Cloud "%s" not supported' % cloud)

        if info:
            self.uid = info['id']
            self.ip = info['ip']
        return self

    def __repr__(self):
        return 'Instance(%s)' % self.to_dict()

    def to_dict(self):
        ret = {}
        ret['id'] = self.uid
        ret['ip'] = self.ip
        return ret

    def get_id(self):
        if self._id is None:
            self._id = self.fetch_id()
        return self._id

    def fetch_id(self):
        raise NotImplementedError()

    def set_id(self, value):
        self._id = value

    uid = property(get_id, set_id, None)

    def get_ip(self):
        if self._ip is None:
            self._ip = self.fetch_ip()
        return self._ip

    def fetch_ip(self):
        raise NotImplementedError()

    def set_ip(self, value):
        self._ip = value

    ip = property(get_ip, set_ip, None)

    def create(self):
        raise NotImplementedError()

    def destroy(self):
        raise NotImplementedError()

    def get_node(self):
        if self._node is None:
            self._node = self.fetch_node()
        return self._node

    def fetch_node(self):
        raise NotImplementedError()

    def set_node(self, value):
        self._node = value

    node = property(get_node, set_node, None)


class BareInstance(Instance):

    def fetch_id(self):
        warnings.warn("Bare Metal instance cannot fetch id", DSBWarning)

    def fetch_ip(self):
        warnings.warn("Bare Metal instance cannot fetch ip address", DSBWarning)

    def fetch_node(self):
        warnings.warn("Bare Metal instance doesnt have a node", DSBWarning)

    def create(self):
        warnings.warn("Bare Metal instances cannot be created", DSBWarning)


class AWSInstance(Instance):

    def fetch_id(self):
        return self.node.id

    def fetch_ip(self):
        return self.node.public_ips[0]

    def fetch_node(self):
        return self.driver.list_nodes(ex_node_ids=[self.uid])[0]

    def create(self):
        name = ''
        ami_id = self.data['image']
        image = NodeImage(id=ami_id, name=None, driver=self.driver)

        ex_keyname = self.data['keyname']
        ex_securitygroup = self.data['security_groups']

        instance_type = self.data['size']
        sizes = self.driver.list_sizes()
        size = [s for s in sizes if s.id == instance_type][0]

        ebs_mapping = [{'DeviceName': '/dev/sda1',
                        'Ebs': {'DeleteOnTermination': 'true',
                                'VolumeSize': 200,
                                'VolumeType': 'gp2'},
                        'VirtualName': None}]

        try:
            node = self.driver.create_node(name=name, size=size, image=image,
                        ex_keyname=ex_keyname, ex_securitygroup=ex_securitygroup,
                        ex_blockdevicemappings=ebs_mapping)
        except Exception, e:
            if 'EBS block device mappings not supported for instance-store AMIs' in str(e):
                node = self.driver.create_node(name=name, size=size, image=image,
                        ex_keyname=ex_keyname, ex_securitygroup=ex_securitygroup)
            else:
                raise(e)

        self.node = node
        return node

    def destroy(self):
        self.node.destroy()


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
        cloud = dsbfile['cloud'].lower()
        if cloud == 'aws':
            return Driver.aws_create(dsbfile)

    @classmethod
    def aws_create(cls, dsbfile):
        cls = get_driver(cls.aws_region_map[dsbfile['region'].lower()])
        return cls(dsbfile['key'], dsbfile['secret'])
