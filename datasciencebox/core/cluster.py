from __future__ import unicode_literals

import os
import shutil

import yaml
from libcloud.compute.types import Provider
from libcloud.compute.base import NodeImage
from libcloud.compute.providers import get_driver

from datasciencebox.core import config

this_dir = os.path.dirname(os.path.realpath(__file__))
f = open(os.path.join(this_dir, 'templates/master.conf'), 'r')
MASTER_CONFIG_TEMPLATE = f.read()
f.close()


def safe_create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def load_clusters():
    cluster_names = [file_ for file_ in os.listdir(config.CLUSTERS_DIR) if
                     os.path.isdir(os.path.join(config.CLUSTERS_DIR, file_))]

    clusters = Clusters()
    for cluster_name in cluster_names:
        p = Cluster.from_directory(cluster_name)
        clusters.append(p)
    return clusters


class Clusters(list):

    def __init__(self, *args, **kwargs):
        self.default = None

    def get(self, name=None):
        if not name:
            return self[0]

        for item in self:
            if item.name == name:
                return item


class Cluster(object):

    def __init__(self, name, profile):
        self.name = name

        self.profile = profile
        self.master = None
        self.minions = []

    def __repr__(self):
        return 'Cluster({0})'.format(self.name)

    @classmethod
    def from_directory(cls, cluster_name):
        from datasciencebox.core.profile import load_profiles

        filepath = os.path.join(config.CLUSTERS_DIR, cluster_name, 'info.yaml')
        with open(filepath, 'r') as f:
            info = yaml.load(f)
            assert len(info.keys()) == 1, 'Should be only one root in cluster yaml file'

            name = info.keys()[0]
            profile = load_profiles().get(info[name]['profile'])
            self = cls(name, profile)

            self.add_master(info[name]['master']['name'], info[name]['master'])
            if 'minions' in info[name]:
                for minion_dict in info[name]['minions']:
                    minion_name = minion_dict.keys()[0]
                    self.add_minion(minion_name, minion_dict[minion_name])

        return self

    def get_directory(self):
        return os.path.join(config.CLUSTERS_DIR, self.name)

    def save_info(self):
        safe_create_dir(self.get_directory())
        filepath = self.get_info_path()
        with open(filepath, 'w') as f:
            yaml.safe_dump(self.to_dict(), f, default_flow_style=False)

    def get_info_path(self):
        return os.path.join(config.CLUSTERS_DIR, self.name, 'info.yaml')

    def to_dict(self):
        ret = {}
        ret['master'] = self.master.to_dict()
        ret['master']['name'] = self.master.name
        ret['minions'] = [{minion.name: minion.to_dict()} for minion in self.minions]
        ret['profile'] = self.profile.name
        ret = { self.name: ret }
        return ret

    def update_config(self):
        self.save_roster()
        self.create_salt_ssh_files()

    def save_roster(self):
        safe_create_dir(self.get_directory())

        def roster_items(instance):
            ret = {}
            ret['host'] = instance.ip
            ret['user'] = instance.profile.user
            ret['priv'] = instance.profile.keypair
            ret['sudo'] = True
            return ret

        ret = {}
        ret[self.master.name] = roster_items(self.master)
        for minion in self.minions:
            ret[minion.name] = roster_items(minion)

        filepath = self.get_roster_path()
        with open(filepath, 'w') as f:
            yaml.safe_dump(ret, f, default_flow_style=False)

    def get_roster_path(self):
        return os.path.join(self.get_directory(), 'roster.yaml')

    def get_pillar_path(self):
        return os.path.join(self.get_directory(), 'pillar')

    def create_salt_ssh_files(self):
        etc_salt_dir = self.get_salt_config_dir()
        safe_create_dir(etc_salt_dir)
        var_salt_dir = os.path.join(self.get_directory(), 'var', 'cache', 'salt')
        safe_create_dir(var_salt_dir)

        srv_pillar_dir = self.get_pillar_path()
        print config.SALT_PILLAR_DIR, srv_pillar_dir
        if os.path.exists(srv_pillar_dir):
            shutil.rmtree(srv_pillar_dir)
        shutil.copytree(config.SALT_PILLAR_DIR, srv_pillar_dir)

        salt_master_config = MASTER_CONFIG_TEMPLATE.format(cachedir=var_salt_dir,
                             file_roots=config.SALT_STATES_DIR,
                             default_pillar_roots=config.SALT_PILLAR_DIR,
                             cluster_pillar_roots=srv_pillar_dir)
        salt_master_file = os.path.join(etc_salt_dir, 'master')
        with open(salt_master_file, 'w') as f:
            f.write(salt_master_config)



    def get_salt_config_dir(self):
        return os.path.join(self.get_directory(), 'etc', 'salt')

    def add_master(self, name=None, info=None):
        if not name:
            name = self.name + '-master'
        self.master = self.instance_type()(name, self.profile)
        if info:
            self.master.from_dict(info)

    def add_minion(self, name=None, info=None):
        if not name:
            i = len(self.minions) + 1
            name = self.name + '-minion-%i' % i
        minion = self.instance_type()(name, self.profile)
        if info:
            minion.from_dict(info)
        self.minions.append(minion)

    def instance_type(self):
        if self.profile.provider.cloud == 'aws':
            return AWSInstance

    def create(self):
        master_node = self.master.create()
        minion_nodes = [minion.create() for minion in self.minions]

        nodes = [master_node] + minion_nodes
        self.profile.provider.driver.wait_until_running(nodes)

        master_node = self.profile.provider.driver.list_nodes(ex_node_ids=[master_node.id])
        self.master.node = master_node[0]

        minion_ids = [node.id for node in minion_nodes]
        new_minion_nodes = self.profile.provider.driver.list_nodes(ex_node_ids=minion_ids)
        for node in new_minion_nodes:
            for instance in self.minions:
                if node.name == instance.name:
                    instance.node = node

    def destroy(self):
        self.master.destroy()
        for minion in self.minions:
            minion.destroy()

    def describe(self):
        ## TODO: Move to cli with a couple of options
        txt = 'Master:\n'
        txt += self.master.describe(indent=2) + '\n'
        if self.minions:
            txt += 'Minion(x%s):\n' % len(self.minions)
            txt += self.minions[0].describe(indent=2)
        return txt


class Instance(object):

    def __init__(self, name, profile):
        self.name = name
        self.profile = profile

        self.ip = None
        self.node = None

    def __repr__(self):
        return 'Instance(%s)' % self.name

    def from_dict(self, info):
        self.ip = info['ip']

    def to_dict(self):
        ret = {}
        ret['ip'] = self.ip
        return ret

    def create(self):
        raise NotImplementedError()

    def destroy(self):
        raise NotImplementedError()


class AWSInstance(Instance):

    def __init__(self, *args, **kwargs):
        super(AWSInstance, self).__init__(*args, **kwargs)

        self._node = None
        self.id = None
        self._ip = None
        self._private_dns = None

    def __repr__(self):
        return 'EC2Instance(%s)' % self.name

    def from_dict(self, info):
        self.id = info['id']
        self.ip = info['ip']
        self.private_dns = info['private_dns']

    def to_dict(self):
        ret = {}
        ret['id'] = self.id
        ret['ip'] = self.ip
        ret['private_dns'] = self.private_dns
        return ret

    def get_ip(self):
        if not self._ip:
            self._ip = self.node.public_ips[0]
        return self._ip

    def set_ip(self, value):
        self._ip = value

    ip = property(get_ip, set_ip, None)

    def get_private_dns(self):
        if not self._private_dns:
            self._private_dns = self.node.extra['private_dns']
        return self._private_dns

    def set_private_dns(self, value):
        self._private_dns = value

    private_dns = property(get_private_dns, set_private_dns, None)

    def get_node(self):
        return self._node

    def set_node(self, value):
        self._node = value
        if value:
            self.id = self._node.id

    node = property(get_node, set_node, None)

    def create(self):
        image = NodeImage(id=self.profile.image, name=None, driver=self.profile.provider.driver)

        sizes = self.profile.provider.driver.list_sizes()
        size = [s for s in sizes if s.id == self.profile.size][0]

        node = self.profile.provider.driver.create_node(name=self.name, size=size, image=image,
                    ex_keyname=self.profile.keyname,
                    ex_securitygroup=self.profile.security_groups)
        self.node = node
        return node

    def destroy(self):
        if not self.node:
            self.fetch_node()

        self.node.destroy()

    def fetch_node(self):
        node = self.profile.provider.driver.list_nodes(ex_node_ids=[self.id])
        self.node = node[0]

    def describe(self, indent=0):
        ## TODO: Move to cli with a couple of options
        txt = ' ' * indent + 'name: ' + self.name + '\n'
        if self._ip:
            txt = ' ' * indent + 'ip: ' + self.ip + '\n'
        txt += ' ' * indent + 'size: ' + self.profile.size + '\n'
        txt += ' ' * indent + 'image: ' + self.profile.image + '\n'
        txt += ' ' * indent + 'keyname: ' + self.profile.keyname + '\n'
        txt += ' ' * indent + 'keypair: ' + self.profile.keypair
        return txt


if __name__ == '__main__':
    c = load_clusters().get()
    c.generate_roster()
