import os
import yaml
import shutil

from datasciencebox.core.settings import Settings
from datasciencebox.core.cloud.cluster import Cluster
from datasciencebox.core.exceptions import DSBException


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
        self.salt_ssh_copy_pillar()

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

    @property
    def roster_path(self):
        return os.path.join(self.settings_dir, 'roster.yaml')

    def create_roster(self):
        with open(self.roster_path, 'w') as f:
            yaml.safe_dump(self.generate_roster(), f, default_flow_style=False)

    def generate_roster(self):
        def roster_item(instance):
            ret = {}
            ret['host'] = instance.ip
            ret['user'] = instance.username
            ret['priv'] = instance.keypair
            ret['sudo'] = True
            return ret

        ret = {}
        ret['master'] = roster_item(self.cluster.instances[0])
        for i, instance in enumerate(self.cluster.instances[1:]):
            ret['minion-%i' % (i + 1)] = roster_item(instance)
        return ret

    @property
    def salt_ssh_config_dir(self):
        return os.path.join(self.settings_dir, 'etc', 'salt')

    def salt_ssh_create_master_conf(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(this_dir, 'templates', 'master.conf')
        with open(template_path, 'r') as f:
            master_conf_template = f.read()

        values = {}
        default_file_roots = os.path.join(this_dir, '..', '..', 'salt')
        values['default_file_roots'] = os.path.realpath(default_file_roots)
        values['extra_file_roots'] = os.path.join(self.settings_dir, 'salt')
        values['pillar_roots'] = self.pillar_dir
        values['root_dir'] = self.settings_dir
        values['cachedir'] = os.path.join(self.settings_dir, 'var', 'cache', 'salt')

        master_conf = master_conf_template.format(**values)
        etc_salt_dir = os.path.join(self.settings_dir, 'etc', 'salt')
        salt_master_file = os.path.join(etc_salt_dir, 'master')
        with open(salt_master_file, 'w') as f:
            f.write(master_conf)

    @property
    def pillar_dir(self):
        return os.path.join(self.settings_dir, 'pillar')

    def salt_ssh_copy_pillar(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        pillar_roots_src = os.path.join(this_dir, '..', '..', 'pillar')
        pillar_roots_src = os.path.realpath(pillar_roots_src)

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


if __name__ == '__main__':
    p = Project.from_dir('../')
    p.create_cluster()
    p.save()

    # p.read()
    # print p.generate_roster()
    # p.update()
    # p.save()
