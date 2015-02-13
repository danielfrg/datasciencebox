import os
import sys
import time
# import subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fabric.api import settings
from fabric.contrib.project import rsync_project

from datasciencebox.core import config


class RsyncHandler(FileSystemEventHandler):
    cluster = None
    base_srv_dst = '/srv'
    base_salt_dst = '/srv/salt'
    base_pillar_dst = '/srv/pillar'
    base_salt_src = config.SALT_STATES_DIR

    def on_modified(self, event):
        event_dir_path = event.src_path
        base_pillar_src = self.cluster.get_pillar_path()

        dst_dir = None
        if event_dir_path.startswith(self.base_salt_src):
            extra_path = event_dir_path[len(self.base_salt_src) + 1:]
            print extra_path
            dst_dir = os.path.join(self.base_salt_dst, extra_path)
        elif event_dir_path.startswith(base_pillar_src):
            extra_path = event_dir_path[len(base_pillar_src) + 1:]
            print extra_path
            dst_dir = os.path.join(self.base_pillar_dst, extra_path)

        src_dir = event_dir_path + '/'
        dst_dir = dst_dir.rstrip('/')
        self.rsync(src_dir, dst_dir)

    def rsync(self, src, dst):
        if os.path.exists(src):
            host_string = '{0}@{1}'.format(self.cluster.master.profile.user, self.cluster.master.ip)
            key_filename = self.cluster.master.profile.keypair
            with settings(host_string=host_string, key_filename=key_filename):
                # print src + ' -> ' + dst
                rsync_project(dst, src, delete=True, extra_opts='--rsync-path="sudo rsync"', exclude='.DS_Store', default_opts='-pthrz')

    def sync_all(self):
        self.rsync(self.base_salt_src, self.base_srv_dst)
        pillar_src = self.cluster.get_pillar_path()
        self.rsync(pillar_src, self.base_srv_dst)


def loop(cluster, handler):
    observer = Observer()
    observer.schedule(handler, config.SALT_STATES_DIR, recursive=True)
    observer.schedule(handler, cluster.get_pillar_path(), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == '__main__':
    from datasciencebox.cli import cli
    cluster = cli.get_cluster()
    handler = RsyncHandler()
    handler.cluster = cluster
    handler.sync_all()
    loop(cluster, handler)
