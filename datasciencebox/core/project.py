import os
import yaml
import shutil

from datasciencebox.core.dsbfile import DSBFile
from datasciencebox.core.cloud import Cluster
from datasciencebox.core.exceptions import DSBException


def safe_create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


class Project(object):

    def __init__(self, cwd=None):
        self.cwd = cwd if cwd else os.getcwd()
        self.cluster = None
        self.dsbfile = None

    @classmethod
    def from_cwd(cls, cwd=None):
        cwd = cwd if cwd else os.getcwd()
        self = cls(cwd=cwd)

        if not os.path.exists(self.dsbfile_path):
            raise DSBException('dsbfile not found')

        self.read_dsbfile()
        self.read_instances()
        return self

    @property
    def dir(self):
        path = os.path.join(self.cwd, '.dsb')
        safe_create_dir(path)
        return os.path.realpath(path)

    @property
    def dsbfile_path(self):
        return os.path.join(self.cwd, 'dsbfile')

    def read_dsbfile(self):
        '''
        Read the dsbfile info
        '''
        fname = 'dsbfile'
        fname_secret = fname + '.secret'

        fpaths = []
        fpaths.append(os.path.join(self.cwd, fname))
        fpaths.append(os.path.join(self.cwd, fname_secret))
        self.dsbfile = DSBFile.from_filepaths(fpaths)

        self.dsbfile.validate_fields()

    def read_instances(self):
        '''
        Read `.dsb/instances.yaml`
        Initiates `self.cluster`
        '''
        filepath = self.instances_path
        if os.path.exists(filepath):
            self.cluster = Cluster.from_filepath(filepath, self.dsbfile)

    def save_instances(self):
        filepath = self.instances_path
        with open(filepath, 'w') as f:
            yaml.safe_dump(self.cluster.to_list(), f, default_flow_style=False)

    @property
    def instances_path(self):
        return os.path.join(self.dir, 'instances.yaml')

    def create(self):
        self.cluster = Cluster()
        self.cluster.dsbfile = self.dsbfile
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
        ret['master'] = roster_item(self.cluster.instances[0])
        for i, instance in enumerate(self.cluster.instances[1:]):
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
    p = Project()
    p.read()
    p.read_instances()
    # print p.generate_roster()
    p.update()
    # p.create()
    # p.save()
