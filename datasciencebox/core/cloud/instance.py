import os
import socket
import warnings

import paramiko
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, SSHException
from libcloud.compute.base import NodeImage

from datasciencebox.core.logger import getLogger
logger = getLogger()
from datasciencebox.core.exceptions import DSBException, DSBWarning
from datasciencebox.core.utils import retry
from datasciencebox.core.ssh import SSHClient

class Instance(object):

    def __init__(self, uid=None, ip=None, port=None, username=None, keypair=None, settings=None, cluster=None):
        logger.debug('Initializing Instance')
        self.settings = settings
        self.cluster = cluster
        self._driver = None
        self._node = None
        self._uid = None
        self._ip = None
        self._port = 22
        self._username = None
        self._keypair = None

        self.uid = uid
        self.ip = ip
        self.port = port
        self.username = username
        self.keypair = keypair

    @classmethod
    def new(cls, settings, *args, **kwargs):
        """
        Create a new Cloud instance based on the Settings
        """
        logger.debug('Initializing new "%s" Instance object' % settings['CLOUD'])
        cloud = settings['CLOUD']
        if cloud == 'bare':
            self = BareInstance(settings=settings, *args, **kwargs)
        elif cloud == 'aws':
            self = AWSInstance(settings=settings, *args, **kwargs)
        elif cloud == 'gcp':
            self = GCPInstance(settings=settings, *args, **kwargs)
        else:
            raise DSBException('Cloud "%s" not supported' % cloud)
        return self

    def __repr__(self):
        return 'Instance(%s)' % self.to_dict()

    def to_dict(self):
        ret = {}
        ret['uid'] = self.uid
        ret['ip'] = self.ip
        ret['port'] = self.port
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
        if value:
            try:
                self._ip, self.port = value.split(":")
            except ValueError:
                self._ip = value

    ip = property(get_ip, set_ip, None)

    def get_port(self):
        return self._port

    def set_port(self, value):
        self._port = value or self.port
        self._port = int(self._port)

    port = property(get_port, set_port, None)

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
        default_username = self.settings['USERNAME'] if self.settings else None
        return self._username or default_username

    def set_username(self, value):
        self._username = value

    username = property(get_username, set_username, None)

    def get_keypair(self):
        default_keypair = self.settings['KEYPAIR'] if self.settings else None
        key = self._keypair or default_keypair
        return os.path.expanduser(key)

    def set_keypair(self, value):
        self._keypair = value

    keypair = property(get_keypair, set_keypair, None)

    def create(self, suffix=None):
        raise NotImplementedError('Subclass of Instance must implement "create"')

    def destroy(self):
        raise NotImplementedError('Subclass of Instance must implement "destroy"')

    @retry(catch=(BadHostKeyException, AuthenticationException, SSHException, socket.error))
    def check_ssh(self):
        logger.debug('Checking ssh connection of %s', self.ip)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.ip, port=self.port, username=self.username, key_filename=self.keypair)
        return True

    def get_ssh_client(self):
        host = self.ip
        username = self.username
        pkey = self.keypair
        port = self.port
        client = SSHClient(host, username=username, pkey=pkey, port=port)
        return client

    ssh_client = property(get_ssh_client, None, None)

class BareInstance(Instance):

    def fetch_uid(self):
        pass

    def fetch_ip(self):
        warnings.warn('Bare Metal instance cannot fetch ip address', DSBWarning)

    def fetch_node(self):
        warnings.warn('Bare Metal instance cannot fetch a node', DSBWarning)

    def create(self, suffix=None):
        warnings.warn('Bare Metal instance cannot be created', DSBWarning)

    def destroy(self):
        warnings.warn('Bare Metal instance cannot be destroyed', DSBWarning)


class AWSInstance(Instance):

    def fetch_uid(self):
        return self.node.id

    def fetch_ip(self):
        return self.node.public_ips[0]

    def fetch_node(self):
        logger.debug('Fetching aws Instance: %s', self.uid)
        return self.driver.list_nodes(ex_node_ids=[self.uid])[0]

    def create(self, suffix=None):
        suffix = '-%s' % suffix if suffix is not None else ''
        name = '%s%s' % (self.settings['ID'], suffix)

        ami_id = self.settings['AWS_IMAGE']
        image = NodeImage(id=ami_id, name=None, driver=self.driver)
        root_size = self.settings['AWS_ROOT_SIZE']
        root_type = self.settings['AWS_ROOT_TYPE']
        ex_keyname = self.settings['AWS_KEYNAME']
        ex_securitygroup = self.settings['AWS_SECURITY_GROUPS']

        instance_type = self.settings['AWS_SIZE']
        sizes = self.driver.list_sizes()
        size = [s for s in sizes if s.id == instance_type][0]

        ebs_mapping = [{
            'DeviceName': '/dev/sda1',
            'Ebs':
            {'DeleteOnTermination': 'true',
             'VolumeSize': root_size,
             'VolumeType': root_type},
            'VirtualName': None
        }]

        try:
            self.node = self.driver.create_node(name=name,
                                                size=size,
                                                image=image,
                                                ex_keyname=ex_keyname,
                                                ex_securitygroup=ex_securitygroup,
                                                ex_blockdevicemappings=ebs_mapping)
        except Exception as e:
            if 'EBS block device mappings not supported for instance-store AMIs' in str(e):
                self.node = self.driver.create_node(name=name,
                                                    size=size,
                                                    image=image,
                                                    ex_keyname=ex_keyname,
                                                    ex_securitygroup=ex_securitygroup)
            else:
                raise (e)

        return self.node

    def destroy(self):
        self.node.destroy()


class GCPInstance(Instance):

    def fetch_uid(self):
        return self.node.id

    def fetch_ip(self):
        return self.node.public_ips[0]

    def fetch_node(self):
        logger.debug('Fetching aws Instance: %s', self.uid)
        all_nodes = self.driver.list_nodes()
        node = [node for node in all_nodes if node.id == self.uid]
        return node[0]

    def create(self, suffix=None):
        suffix = '-%s' % suffix if suffix is not None else ''
        name = '%s%s' % (self.settings['ID'], suffix)
        image = self.settings['GCP_IMAGE']
        size = self.settings['GCP_SIZE']
        network = self.settings['GCP_NETWORK']
        root_disk_size = self.settings['GCP_ROOT_SIZE']
        root_disk_type = self.settings['GCP_ROOT_TYPE']

        metadata = {}
        with open(os.path.expanduser(self.settings['GCP_PUBLIC_KEY'])) as f:
            metadata['sshKeys'] = '%s:%s' % (self.settings['USERNAME'], f.read())

        volume = self.driver.create_volume(size=root_disk_size,
                                           name=name,
                                           ex_disk_type=root_disk_type,
                                           image=image)

        sa_scopes = [{'scopes': ['compute', 'storage-full']}]
        self.node = self.driver.create_node(name=name,
                                            size=size,
                                            image=image,
                                            ex_metadata=metadata,
                                            ex_network=network,
                                            ex_boot_disk=volume,
                                            ex_disk_auto_delete=True,
                                            ex_service_accounts=sa_scopes)
        return self.node

    def destroy(self):
        self.node.destroy()
