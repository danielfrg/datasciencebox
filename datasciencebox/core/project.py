import os
import yaml
import shutil

from datasciencebox.core.logger import getLogger
logger = getLogger()
from datasciencebox.core import salt
from datasciencebox.core import utils
from datasciencebox.core.settings import Settings
from datasciencebox.core.cloud.cluster import Cluster
from datasciencebox.core.exceptions import DSBException


class Project(object):
    """
    Main DataScienceBox entrypoint.

    Manages all the IO to and from files.
    """

    @classmethod
    def from_dir(cls, path=os.getcwd(), settingsfile='dsbfile'):
        dir_ = path
        while dir_ != '/':
            if os.path.exists(os.path.join(settingsfile, dir_)):
                logger.debug('"{}" FOUND on "{}"'.format(settingsfile, dir_))
                break
            logger.debug('"{}" not found on "{}" trying parent directory'.format(settingsfile, dir_))
            dir_ = os.path.abspath(os.path.join(dir_, os.pardir))

        if not os.path.exists(os.path.join(dir_, 'dsbfile')):
            raise DSBException('"{}" not found on ""{}" or its parents'.format(settingsfile, path))

        return cls.from_file(filepath=os.path.join(dir_, settingsfile))

    @classmethod
    def from_file(cls, filepath):
        dir_ = os.path.dirname(filepath)
        settingsfile = os.path.basename(filepath)

        self = cls(path=dir_, settingsfile=settingsfile)
        logger.debug('Starting project from: %s' % filepath)
        self.read_settings()
        self.read_instances()
        return self

    def __init__(self, path=None, settingsfile='dsbfile'):
        self.dir = path
        self.settingsfile = settingsfile
        self.cluster = None
        self.settings = None

    @property
    def settings_path(self):
        return os.path.join(self.dir, self.settingsfile)

    @property
    def settings_dir(self):
        """
        Directory that contains the the settings for the project
        """
        path = os.path.join(self.dir, '.dsb')
        utils.create_dir(path)
        return os.path.realpath(path)

    def read_settings(self):
        """
        Read the "dsbfile" file
        Populates `self.settings`
        """
        logger.debug('Reading settings from: %s' % self.settings_path)
        self.settings = Settings.from_dsbfile(self.settings_path)

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
        self.salt_ssh()

    # --------------------------------------------------------------------------
    # Salt
    # --------------------------------------------------------------------------

    def salt(self, module, target='*', args=None, kwargs=None, ssh=False):
        """
        Execute a salt (or salt-ssh) command
        """
        if ssh:
            return salt.salt_ssh(self, target, module, args, kwargs)
        else:
            return salt.salt_master(self, target, module, args, kwargs)

    @property
    def roster_path(self):
        return os.path.join(self.settings_dir, 'roster.yaml')

    @property
    def salt_dir(self):
        return os.path.join(self.settings_dir, 'salt')

    @property
    def pillar_dir(self):
        return os.path.join(self.settings_dir, 'pillar')

    @property
    def salt_ssh_config_dir(self):
        return os.path.join(self.settings_dir, 'etc', 'salt')

    def salt_ssh(self):
        """
        Setup `salt-ssh`
        """
        self.create_roster_file()
        self.salt_ssh_create_dirs()
        self.salt_ssh_create_master_file()
        self.copy_salt_and_pillar()

    def create_roster_file(self):
        logger.debug('Creating roster file to: %s' % self.roster_path)
        with open(self.roster_path, 'w') as f:
            dict_ = salt.generate_roster(self.cluster)
            yaml.safe_dump(dict_, f, default_flow_style=False)

    def salt_ssh_create_dirs(self):
        """
        Creates the `salt-ssh` required directory structure
        """
        logger.debug('Creating salt-ssh dirs into: %s' % self.settings_dir)
        utils.create_dir(os.path.join(self.settings_dir, 'salt'))
        utils.create_dir(os.path.join(self.settings_dir, 'pillar'))
        utils.create_dir(os.path.join(self.settings_dir, 'etc', 'salt'))
        utils.create_dir(os.path.join(self.settings_dir, 'var', 'cache', 'salt'))
        utils.create_dir(os.path.join(self.settings_dir, 'var', 'log', 'salt'))

    def salt_ssh_create_master_file(self):
        etc_salt_dir = os.path.join(self.settings_dir, 'etc', 'salt')
        master_conf_file = os.path.join(etc_salt_dir, 'master')
        with open(master_conf_file, 'w') as f:
            dict_ = salt.generate_salt_ssh_master_conf(project=self)
            yaml.safe_dump(dict_, f, default_flow_style=False)

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

        ip = self.cluster.master.ip
        utils.replace_all(os.path.join(self.pillar_dir, 'salt.sls'), 'localhost', ip)
        utils.replace_all(os.path.join(self.pillar_dir, 'system.sls'), 'vagrant',
                          self.settings['USERNAME'])


if __name__ == '__main__':
    p = Project.from_dir('../../')
    p.create_cluster()
    p.save_instances()
