import os
import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fabric.api import settings, sudo, hide
from fabric.contrib.project import rsync_project


class RsyncHandler(FileSystemEventHandler):
    project = None
    dst_default_file_root = '/srv/salt/base'
    dst_extra_file_root = '/srv/salt/extra'
    dst_pillar_root = '/srv/pillar'

    def on_modified(self, event):
        modified_file = os.path.realpath(event.src_path)
        src_dir = os.path.realpath(os.path.dirname(modified_file))

        this_dir = os.path.dirname(os.path.realpath(__file__))
        default_file_root = os.path.realpath(os.path.join(this_dir, '..', '..', 'salt'))
        extra_file_root = os.path.join(self.project.dir, 'salt')
        pillar_root = self.project.pillar_dir

        if modified_file.startswith(default_file_root):
            extra_path = src_dir[len(default_file_root) + 1:]
            dst_dir = self.dst_default_file_root
        elif modified_file.startswith(extra_file_root):
            extra_path = src_dir[len(extra_file_root) + 1:]
            dst_dir = self.dst_extra_file_root
        elif modified_file.startswith(pillar_root):
            extra_path = src_dir[len(pillar_root) + 1:]
            dst_dir = self.dst_pillar_root
        else:
            raise Exception('Weird source path')

        dst_dir = os.path.join(dst_dir, extra_path)
        src_dir = src_dir.rstrip('/')
        dst_dir = dst_dir.rstrip('/')
        self.rsync(src_dir, dst_dir)

    def rsync(self, src, dst):
        src = os.path.realpath(src) + '/'
        dst = os.path.realpath(dst)
        if os.path.exists(src):
            host_string = '{0}@{1}'.format(self.project.dsbfile['user'], self.project.cloud.master.ip)
            key_filename = self.project.dsbfile['keypair']
            with hide('running', 'stdout', 'stderr'):
                with settings(host_string=host_string, key_filename=key_filename):
                    print src + ' -> ' + dst
                    rsync_project(dst, src, delete=True, extra_opts='--rsync-path="sudo rsync"', exclude='.DS_Store', default_opts='-pthrz')

    def sync_all(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        default_file_root = os.path.join(this_dir, '..', '..', 'salt')
        extra_file_root = os.path.join(self.project.dir, 'salt')
        pillar_root = self.project.pillar_dir

        self.rsync(default_file_root, self.dst_default_file_root)
        self.rsync(extra_file_root, self.dst_extra_file_root)
        self.rsync(pillar_root, self.dst_pillar_root)


def loop(project, handler):
    this_dir = os.path.dirname(os.path.realpath(__file__))

    default_file_root = os.path.join(this_dir, '..', '..', 'salt')
    extra_file_root = os.path.join(project.dir, 'salt')
    pillar_root = project.pillar_dir

    observer = Observer()
    observer.schedule(handler, default_file_root, recursive=True)
    observer.schedule(handler, extra_file_root, recursive=True)
    observer.schedule(handler, pillar_root, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == '__main__':
    from datasciencebox.core.main import Project
    project = Project.from_cwd('../core')
    handler = RsyncHandler()
    handler.project = project
    # handler.sync_all()
    loop(project, handler)
