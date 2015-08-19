import os
import sys
import yaml
import shutil
import fileinput

from datasciencebox.core.logger import getLogger
logger = getLogger()
from datasciencebox.core import salt
from datasciencebox.core.settings import Settings
from datasciencebox.core.cloud.cluster import Cluster
from datasciencebox.core.exceptions import DSBException


def safe_create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


class Project(object):

    @classmethod
    def from_dir(cls, path=os.getcwd()):
        logger.debug('Starting project from: %s' % path)
        self = cls(path=path)

        if not os.path.exists(self.settings_path):
            raise DSBException('"dsbfile" not found on %s' % path)

        self.read_settings()
        self.read_instances()
        return self

    def __init__(self, path=None):
        self.dir = path
        self.cluster = None
        self.settings = None

    @property
    def settings_path(self):
        return os.path.join(self.dir, 'dsbfile')

    @property
    def settings_dir(self):
        """
        Directory that contains the instances.yaml and other stuff
        """
        path = os.path.join(self.dir, '.dsb')
        safe_create_dir(path)
        return os.path.realpath(path)

    def read_settings(self):
        """
        Read the settings "dsbfile" file
        Populates `self.settings`
        """
        logger.debug('Reading settings from: %s' % self.settings_path)
        if os.path.exists(self.settings_path):
            self.settings = Settings.from_dsbfile(self.settings_path)
        else:
            pass # TODO: do something?

    def read_instances(self):
        """
        Read `.dsb/instances.yaml`
        Populates `self.cluster`
        """
        logger.debug('Reading instances from: %s' % self.instances_path)
        if os.path.exists(self.instances_path):
            with open(self.instances_path, 'r') as f:
                list_ = yaml.load(f.read())
                self.cluster = Cluster.from_list(list_, settings=self.settings)

    def save_instances(self):
        logger.debug('Saving instances file to: %s' % self.instances_path)
        with open(self.instances_path, 'w') as f:
            yaml.safe_dump(self.cluster.to_list(), f, default_flow_style=False)

    @property
    def instances_path(self):
        return os.path.join(self.settings_dir, 'instances.yaml')

    def create_cluster(self):
        self.cluster = Cluster(settings=self.settings)
        self.cluster.create()

    def destroy(self):
        self.cluster.fetch_nodes()
        self.cluster.destroy()

    def update(self, force=False):
        self.create_roster()
        self.salt_ssh_create_dirs()
        self.salt_ssh_create_master_conf()
        self.copy_salt_and_pillar()

    # --------------------------------------------------------------------------
    # Salt-SSH
    # --------------------------------------------------------------------------

    def salt_ssh_create_dirs(self):
        logger.debug('Creating salt-ssh dirs into: %s' % self.settings_dir)
        safe_create_dir(os.path.join(self.settings_dir, 'salt'))
        safe_create_dir(os.path.join(self.settings_dir, 'pillar'))
        safe_create_dir(os.path.join(self.settings_dir, 'etc', 'salt'))
        safe_create_dir(os.path.join(self.settings_dir, 'var', 'cache', 'salt'))
        safe_create_dir(os.path.join(self.settings_dir, 'var', 'log', 'salt'))

    @property
    def roster_path(self):
        return os.path.join(self.settings_dir, 'roster.yaml')

    def create_roster(self):
        logger.debug('Creating roster file to: %s' % self.roster_path)
        with open(self.roster_path, 'w') as f:
            yaml.safe_dump(salt.generate_roster(self.cluster), f, default_flow_style=False)

    @property
    def salt_ssh_config_dir(self):
        return os.path.join(self.settings_dir, 'etc', 'salt')

    def salt_ssh_create_master_conf(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(this_dir, 'templates', 'master.conf')
        with open(template_path, 'r') as f:
            master_conf_template = f.read()

        values = {}
        values['salt_root'] = self.salt_dir
        values['pillar_root'] = self.pillar_dir
        values['root_dir'] = self.settings_dir
        values['cachedir'] = os.path.join(self.settings_dir, 'var', 'cache', 'salt')

        master_conf = master_conf_template.format(**values)
        etc_salt_dir = os.path.join(self.settings_dir, 'etc', 'salt')
        salt_master_file = os.path.join(etc_salt_dir, 'master')
        with open(salt_master_file, 'w') as f:
            f.write(master_conf)

    @property
    def salt_dir(self):
        return os.path.join(self.settings_dir, 'salt')

    @property
    def pillar_dir(self):
        return os.path.join(self.settings_dir, 'pillar')

    def copy_salt_and_pillar(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        salt_roots_src = os.path.join(this_dir, '..', 'salt')
        salt_roots_src = os.path.realpath(salt_roots_src)
        pillar_roots_src = os.path.join(this_dir, '..', 'pillar')
        pillar_roots_src = os.path.realpath(pillar_roots_src)

        if os.path.exists(self.salt_dir):
            shutil.rmtree(self.salt_dir)
        shutil.copytree(salt_roots_src, self.salt_dir)

        if os.path.exists(self.pillar_dir):
            shutil.rmtree(self.pillar_dir)
        shutil.copytree(pillar_roots_src, self.pillar_dir)

        self.replace_all(os.path.join(self.pillar_dir, 'salt.sls'), 'salt-master', self.cluster.master.ip )

    @staticmethod
    def replace_all(file, searchExp, replaceExp):
        for line in fileinput.input(file, inplace=1):
            if searchExp in line:
                line = line.replace(searchExp, replaceExp)
            sys.stdout.write(line)

    def salt(self, module, args=None, kwargs=None, target='*', ssh=False):
        if ssh:
            salt.salt_ssh(self, target, module, args, kwargs)
        else:
            salt.salt_master(self, target, module, args, kwargs)


if __name__ == '__main__':
    p = Project.from_dir('../../')
    p.create_cluster()
    p.save_instances()
