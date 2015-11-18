import os
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class RsyncHandler(FileSystemEventHandler):
    project = None
    dst_salt_root = '/srv/salt'
    dst_pillar_root = '/srv/pillar'

    def on_modified(self, event):
        modified_file = os.path.realpath(event.src_path)
        src_dir = os.path.realpath(os.path.dirname(modified_file))

        salt_file_root = self.project.salt_dir
        pillar_root = self.project.pillar_dir

        if modified_file.startswith(salt_file_root):
            extra_path = src_dir[len(salt_file_root) + 1:]
            dst_dir = self.dst_salt_root
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
            client = self.project.cluster.head.ssh_client
            client.put(src, dst, sudo=True)

    def sync_all(self):
        salt_root = self.project.salt_dir
        pillar_root = self.project.pillar_dir

        self.rsync(salt_root, self.dst_salt_root)
        self.rsync(pillar_root, self.dst_pillar_root)


def loop(project, handler):
    salt_root = project.salt_dir
    pillar_root = project.pillar_dir

    observer = Observer()
    observer.schedule(handler, salt_root, recursive=True)
    observer.schedule(handler, pillar_root, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
