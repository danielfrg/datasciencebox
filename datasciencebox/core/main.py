import os
import yaml
import shutil

from libcloud.compute.base import NodeImage
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


def safe_create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


class Project(object):

    def __init__(self, cwd=None):
        self.cwd = cwd if cwd else os.getcwd()
        self.cloud = None
        self.dsbfile = None

    @classmethod
    def from_cwd(cls, cwd=None):
        cwd = cwd if cwd else os.getcwd()
        self = cls(cwd=cwd)
        self.dsbfile = DSBFile.from_cwd(cwd=cwd)
        self.dsbfile.validate_fields()
        self.read()
        self.read_instances()
        return self

    @property
    def dir(self):
        path = os.path.join(self.cwd, '.dsb')
        safe_create_dir(path)
        return os.path.realpath(path)

    def read(self):
        self.dsbfile = DSBFile.from_cwd(cwd=self.cwd)
        self.dsbfile.validate_fields()

    def read_instances(self):
        filepath = os.path.join(self.dir, 'instances.yaml')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                instances =  yaml.load(f.read())
                self.cloud = Cloud()
                self.cloud.instances = []
                for instance in instances:
                    new_instance = Instance(self.dsbfile)
                    new_instance.from_dict(instance)
                    self.cloud.instances.append(new_instance)

    def create(self):
        self.cloud = Cloud()
        self.cloud.info = self.dsbfile
        self.cloud.create()

    def update(self, force=False):
        self.create_roster()
        self.salt_ssh_create_dirs()
        self.salt_ssh_create_master_conf()
        self.salt_ssh_copy_pillar()

    def save(self):
        # Instances.yaml
        filepath = os.path.join(self.dir, 'instances.yaml')
        with open(filepath, 'w') as f:
            yaml.safe_dump(self.cloud.to_dict(), f, default_flow_style=False)

    # Salt-SSH
    def salt_ssh_create_dirs(self):
        safe_create_dir(os.path.join(self.dir, 'salt'))
        safe_create_dir(os.path.join(self.dir, 'pillar'))
        safe_create_dir(os.path.join(self.dir, 'etc', 'salt'))
        safe_create_dir(os.path.join(self.dir, 'var', 'cache', 'salt'))

    @property
    def roster_path(self):
        return os.path.join(self.dir, 'roster.yaml')

    def create_roster(self):
        with open(self.roster_path, 'w') as f:
            yaml.safe_dump(self.generate_roster(), f, default_flow_style=False)

    def generate_roster(self):
        def roster_item(instance):
            ret = {}
            ret['host'] = instance.ip
            ret['user'] = instance.data['user']
            ret['priv'] = instance.data['keypair']
            ret['sudo'] = True
            return ret

        ret = {}
        ret['master'] = roster_item(self.cloud.instances[0])
        for i, instance in enumerate(self.cloud.instances[1:]):
            ret['minion-%i' % (i + 1)] = roster_item(instance)
        return ret

    @property
    def salt_ssh_config_dir(self):
        return os.path.join(self.dir, 'etc', 'salt')

    def salt_ssh_create_master_conf(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(this_dir, 'templates', 'master.conf')
        with open(template_path, 'r') as f:
            master_conf_template = f.read()

        values = {}
        default_file_roots = os.path.join(this_dir, '..', '..', 'salt')
        values['default_file_roots'] = os.path.realpath(default_file_roots)
        values['extra_file_roots'] = os.path.join(self.dir, 'salt')
        values['pillar_roots'] = self.pillar_dir
        values['root_dir'] = self.dir
        values['cachedir'] = os.path.join(self.dir, 'var', 'cache', 'salt')

        master_conf = master_conf_template.format(**values)
        etc_salt_dir = os.path.join(self.dir, 'etc', 'salt')
        salt_master_file = os.path.join(etc_salt_dir, 'master')
        with open(salt_master_file, 'w') as f:
            f.write(master_conf)

    @property
    def pillar_dir(self):
        return os.path.join(self.dir, 'pillar')

    def salt_ssh_copy_pillar(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        pillar_roots_src = os.path.join(this_dir, '..', '..', 'pillar')
        pillar_roots_src = os.path.realpath(pillar_roots_src)

        if os.path.exists(self.pillar_dir):
            shutil.rmtree(self.pillar_dir)
        shutil.copytree(pillar_roots_src, self.pillar_dir)


class Cloud(object):
    def __init__(self):
        self._driver = None
        self.info = None
        self.instances = []

    @property
    def master(self):
        return self.instances[0]

    @property
    def driver(self):
        if self._driver is None:
            self._driver = Driver.create(self.info)
        return self._driver

    def create(self):
        master_ins = Instance(driver=self.driver, data=self.info)
        instances = [master_ins]

        if 'minion' in self.info:
            number = self.info['minion']['number']
            minions =  [Instance(driver=self.driver, data=self.info) for i in range(number)]
            instances.extend(minions)

        _ = [instance.create() for instance in instances]
        nodes = [instance.node for instance in instances]
        self.driver.wait_until_running(nodes)

        new_nodes = self.driver.list_nodes(ex_node_ids=[node.id for node in nodes])
        for instance, node in zip(instances, new_nodes):
            instance.node = node
        self.instances = instances
        return instances

    def to_dict(self):
        ret = []
        for instance in self.instances:
            ret.append(instance.to_dict())
        return ret


class Instance(object):

    def __init__(self, data, driver=None):
        self.data = data
        self.driver = driver

        self.id = None
        self._node = None
        self._ip = None
        # self._private_dns = None

    def from_dict(self, info):
        self.id = info['id']
        self.ip = info['ip']

    def to_dict(self):
        ret = {}
        ret['id'] = self.id
        ret['ip'] = self.ip
        return ret

    def get_ip(self):
        if not self._ip:
            self._ip = self.node.public_ips[0]
        return self._ip

    def set_ip(self, value):
        self._ip = value

    ip = property(get_ip, set_ip, None)

    def get_node(self):
        if not self._node:
            self.node_ = self.fetch_node()
        return self._node

    def fetch_node(self):
        node = self.driver.list_nodes(ex_node_ids=[self.id])
        self.node = node[0]

    def set_node(self, value):
        self._node = value
        if value:
            self.id = self._node.id

    node = property(get_node, set_node, None)

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
                                'VolumeType': 'standard'},
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
    def create(cls, data):
        cloud = data['cloud'].lower()
        if cloud == 'aws':
            return Driver.aws_create(data)

    @classmethod
    def aws_create(cls, data):
        cls = get_driver(cls.aws_region_map[data['region'].lower()])
        return cls(data['key'], data['secret'])


class DSBFile(dict):

    def validate_fields(self):
        for field in self.required_fields:
            assert field in self, 'Required field "%s" not found' % field
        return True

    @property
    def required_fields(self):
        if self['cloud'] == 'aws':
            return ['key', 'secret', 'keypair', 'keyname', 'security_groups', 'image', 'size', 'user']

    @classmethod
    def from_cwd(cls, cwd=None, fname=None):
        cwd = cwd if cwd else os.getcwd()
        fname = 'dsbfile' if fname is None else fname
        fname_secret = fname + '.secret'

        fpaths = []
        fpaths.append(os.path.join(cwd, fname))
        fpaths.append(os.path.join(cwd, fname_secret))

        instance = cls()
        for fpath in fpaths:
            if os.path.exists(fpath):
                with open(fpath, 'r') as f:
                    dict_ = yaml.load(f.read())
                    instance.update(dict_)

        instance.validate_fields()
        return instance


if __name__ == '__main__':
    p = Project()
    p.read()
    p.read_instances()
    # print p.generate_roster()
    p.update()
    # p.create()
    # p.save()
