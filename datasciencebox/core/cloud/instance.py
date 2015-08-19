import os
import warnings

from libcloud.compute.base import NodeImage

from datasciencebox.core.logger import getLogger
logger = getLogger()
from datasciencebox.core.cloud.driver import Driver
from datasciencebox.core.exceptions import DSBException, DSBWarning


class Instance(object):

    def __init__(self, settings, cluster=None):
        logger.debug('Initializing Instance')
        self.settings = settings
        self.cluster = cluster
        self._driver = None
        self._node = None
        self._uid = None
        self._ip = None
        self._username = None
        self._keypair = None

    @classmethod
    def new(cls, settings, cluster=None):
        """
        Create a new Cloud instance based on the Settings
        """
        logger.debug('Creating new "%s" Instance' % settings['CLOUD'])
        cloud = settings['CLOUD']
        if cloud == 'bare':
            self = BareInstance(settings, cluster=cluster)
        elif cloud == 'aws':
            self = AWSInstance(settings, cluster=cluster)
        elif cloud == 'gcp':
            self = GCPInstance(settings, cluster=cluster)
        else:
            raise DSBException('Cloud "%s" not supported' % cloud)
        return self

    @classmethod
    def from_uid(cls, uid, settings=None, cluster=None):
        """
        Fetch a Cloud instance based on the UniqueID
        """
        self = cls.new(settings=settings, cluster=cluster)
        self.uid = uid
        return self

    @classmethod
    def from_dict(cls, values, settings=None, cluster=None):
        self = cls.new(settings=settings, cluster=cluster)
        self.uid = values['id']
        self.ip = values['ip']
        return self

    def __repr__(self):
        return 'Instance(%s)' % self.to_dict()

    def to_dict(self):
        ret = {}
        ret['id'] = self.uid
        ret['ip'] = self.ip
        return ret

    def get_driver(self):
        return self.cluster.driver

    driver = property(get_driver, None, None)

    def get_uid(self):
        if self._uid is None:
            self._uid = self.fetch_uid()
        return self._uid

    def fetch_uid(self):
        raise NotImplementedError()

    def set_uid(self, value):
        self._uid = value

    uid = property(get_uid, set_uid, None)

    def get_ip(self):
        if self._ip is None:
            self._ip = self.fetch_ip()
        return self._ip

    def fetch_ip(self):
        raise NotImplementedError('Subclass of Instance must implement "fetch_ip"')

    def set_ip(self, value):
        self._ip = value

    ip = property(get_ip, set_ip, None)

    def get_node(self):
        if self._node is None:
            self._node = self.fetch_node()
        return self._node

    def fetch_node(self):
        raise NotImplementedError('Subclass of Instance must implement "fetch_node"')

    def set_node(self, value):
        self._node = value

    node = property(get_node, set_node, None)

    def get_username(self):
        if self._username is None:
            self._username = self.settings['USERNAME']
        return self._username

    def set_username(self, value):
        self._username = value

    username = property(get_username, set_username, None)

    def get_keypair(self):
        if self._keypair is None:
            self._keypair = self.settings['KEYPAIR']
        return self._keypair

    def set_keypair(self, value):
        self._keypair = value

    keypair = property(get_keypair, set_keypair, None)

    def create(self):
        raise NotImplementedError('Subclass of Instance must implement "create"')

    def destroy(self):
        raise NotImplementedError('Subclass of Instance must implement "destroy"')


class BareInstance(Instance):

    def fetch_uid(self):
        warnings.warn('Bare Metal instance cannot fetch id', DSBWarning)

    def fetch_ip(self):
        warnings.warn('Bare Metal instance cannot fetch ip address', DSBWarning)

    def fetch_node(self):
        warnings.warn('Bare Metal instance cannot fetch a node', DSBWarning)

    def create(self):
        warnings.warn('Bare Metal instance cannot be created', DSBWarning)

    def destroy(self):
        warnings.warn('Bare Metal instance cannot be destroyed', DSBWarning)

class AWSInstance(Instance):

    def fetch_uid(self):
        return self.node.id

    def fetch_ip(self):
        return self.node.public_ips[0]

    def fetch_node(self):
        logger.debug('Fetching aws Instance: %s' % self.uid)
        return self.driver.list_nodes(ex_node_ids=[self.uid])[0]

    def create(self):
        name = ''
        ami_id = self.settings['AWS_IMAGE']
        image = NodeImage(id=ami_id, name=None, driver=self.driver)

        ex_keyname = self.settings['AWS_KEYNAME']
        ex_securitygroup = self.settings['AWS_SECURITY_GROUPS']

        instance_type = self.settings['AWS_SIZE']
        sizes = self.driver.list_sizes()
        size = [s for s in sizes if s.id == instance_type][0]

        ebs_mapping = [{'DeviceName': '/dev/sda1',
                        'Ebs': {'DeleteOnTermination': 'true',
                                'VolumeSize': 200,
                                'VolumeType': 'gp2'},
                        'VirtualName': None}]

        try:
            self.node = self.driver.create_node(name=name, size=size, image=image,
                        ex_keyname=ex_keyname, ex_securitygroup=ex_securitygroup,
                        ex_blockdevicemappings=ebs_mapping)
        except Exception, e:
            if 'EBS block device mappings not supported for instance-store AMIs' in str(e):
                self.node = self.driver.create_node(name=name, size=size, image=image,
                            ex_keyname=ex_keyname, ex_securitygroup=ex_securitygroup)
            else:
                raise(e)

        return self.node

    def destroy(self):
        self.node.destroy()


class GCPInstance(Instance):

    def fetch_uid(self):
        return self.node.id

    def fetch_ip(self):
        return self.node.public_ips[0]

    def fetch_node(self):
        logger.debug('Fetching aws Instance: %s' % self.uid)
        all_nodes = self.driver.list_nodes()
        node = [node for node in all_nodes if node.id == self.uid]
        return node[0]

    def create(self, suffix=''):
        suffix = '-%s' % suffix if suffix is not None else ''
        name = '%s%s' % (self.settings['ID'], suffix)
        image = self.settings['GCP_IMAGE']
        size = self.settings['GCP_SIZE']
        network = self.settings['GCP_NETWORK']

        metadata = {}
        with open(os.path.expanduser(self.settings['GCP_PUBLIC_KEY'])) as f:
            metadata['sshKeys'] = '%s:%s' % (self.settings['USERNAME'], f.read())

        self.node = self.driver.create_node(name=name, size=size, image=image,
                                ex_metadata=metadata, ex_network=network)
        return self.node

    def destroy(self):
        self.node.destroy()
