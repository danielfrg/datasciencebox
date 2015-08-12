import os
import yaml
import shutil

from datasciencebox.core.settings import Settings
from datasciencebox.core.cloud.cluster import Cluster
from datasciencebox.core.exceptions import DSBException
from datasciencebox.core import salt


def safe_create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


class Project(object):

    @classmethod
    def from_dir(cls, path=os.getcwd()):
        self = cls(path=path)

        if not os.path.exists(self.settings_path):
            raise DSBException('settings not found')

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
        if os.path.exists(self.settings_path):
            self.settings = Settings.from_dsbfile(self.settings_path)
        else:
            pass # TODO: do something?

    def read_instances(self):
        """
        Read `.dsb/instances.yaml`
        Populates `self.cluster`
        """
        if os.path.exists(self.instances_path):
            with open(self.instances_path, 'r') as f:
                list_ = yaml.load(f.read())
                self.cluster = Cluster.from_list(list_, settings=self.settings)
        else:
            pass # TODO: do something?

    def save_instances(self):
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

    def save(self):
        self.save_instances()

    # --------------------------------------------------------------------------
    # Salt-SSH
    # --------------------------------------------------------------------------

    def salt_ssh_create_dirs(self):
        safe_create_dir(os.path.join(self.settings_dir, 'salt'))
        safe_create_dir(os.path.join(self.settings_dir, 'pillar'))
        safe_create_dir(os.path.join(self.settings_dir, 'etc', 'salt'))
        safe_create_dir(os.path.join(self.settings_dir, 'var', 'cache', 'salt'))
        safe_create_dir(os.path.join(self.settings_dir, 'var', 'log', 'salt'))

    @property
    def roster_path(self):
        return os.path.join(self.settings_dir, 'roster.yaml')

    def create_roster(self):
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
        self.render_pillar('salt.sls', {'master': self.cluster.master.ip })

    def render_pillar(self, path, values):
        from jinja2 import Environment, FileSystemLoader
        pillar_loader = FileSystemLoader(searchpath=self.pillar_dir)
        pillar_env = Environment(loader=pillar_loader)
        pillar_template = pillar_env.get_template(path)
        rendered = pillar_template.render(**values)
        with open(os.path.join(self.pillar_dir, path), 'w') as f:
            f.write(rendered)

    def salt(self, module, args=None, kwargs=None, target='*', ssh=False):
        if ssh:
            salt.salt_ssh(self, target, module, args, kwargs)
        else:
            salt.salt_master(self, target, module, args, kwargs)


if __name__ == '__main__':
    p = Project.from_dir('../')
    p.create_cluster()
    p.save()

    # p.read()
    # print p.generate_roster()
    # p.update()
    # p.save()
