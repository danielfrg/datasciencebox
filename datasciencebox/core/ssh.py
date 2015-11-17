"""
Wrapper around paramiko.SSHClient
"""
import os
import time
import posixpath
from socket import gaierror as sock_gaierror, error as sock_error

import paramiko

from datasciencebox.core.logger import getLogger
logger = getLogger()


class SSHClient(object):

    def __init__(self, host, username=None, password=None, pkey=None, port=22,
                 timeout=15):
        self.host = host
        self.username = username
        self.password = password
        if os.path.isfile(os.path.expanduser(pkey)):
            self.pkey = paramiko.RSAKey.from_private_key_file(pkey)
        else:
            self.pkey = pkey
        self.port = port
        self.timeout = timeout

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        self._sftp = None

        self.connect()

    def connect(self):
        """Connect to host
        """
        try:
            self.client.connect(self.host, username=self.username,
                           password=self.password, port=self.port,
                           pkey=self.pkey, timeout=self.timeout)
        except sock_gaierror, ex:
            raise Exception("Unknown host '%s'" % self.host)
        except sock_error, ex:
            raise Exception("Error connecting to host '%s:%s'\n%s" % (self.host, self.port, ex))
        except paramiko.AuthenticationException, ex:
            msg = "Host is '%s:%s'"
            raise Exception("Authentication Error to host '%s'" % self.host)
        except paramiko.SSHException, ex:
            msg = "General SSH error - %s" % ex
            raise Exception(msg)

    def close(self):
        self.client.close()

    def exec_command(self, command, sudo=False, **kwargs):
        """Wrapper to paramiko.SSHClient.exec_command
        """
        channel = self.client.get_transport().open_session()
        # stdin = channel.makefile('wb')
        stdout = channel.makefile('rb')
        stderr = channel.makefile_stderr('rb')

        if sudo:
            command = 'sudo -S bash -c \'%s\'' % command
        else:
            command = 'bash -c \'%s\'' % command

        logger.debug("Running command %s on '%s'", command, self.host)
        channel.exec_command(command, **kwargs)

        while not (channel.recv_ready() or channel.closed or
                   channel.exit_status_ready()):
            time.sleep(.2)

        ret = {'stdout': stdout.read(), 'stderr': stderr.read(),
               'exit_code': channel.recv_exit_status()}
        return ret

    def get_sftp(self):
        if self._sftp is None:
            self._sftp = self.make_sftp()
        return self._sftp

    def make_sftp(self):
        """Make SFTP client from open transport"""
        transport = self.client.get_transport()
        transport.open_session()
        return paramiko.SFTPClient.from_transport(transport)

    sftp = property(get_sftp, None, None)

    def put(self, local, remote):
        """Copy local file to host via SFTP/SCP

        Copy is done natively using SFTP/SCP version 2 protocol, no scp command
        is used or required.
        """
        if os.path.isdir(local):
            return self._put_dir(local, remote)

        directory = posixpath.dirname(remote)

        try:
            self.sftp.stat(directory)
            self.sftp.chdir(directory)
        except IOError:
            self.mkdir(directory)

        try:
            self.sftp.put(local, remote)
        except Exception, error:
            logger.error("Error occured copying file %s to remote destination %s:%s - %s",
                         local, self.host, remote, error)
        else:
            logger.info("Copied local file %s to remote destination %s:%s",
                        local, self.host, remote)

    def _put_dir(self, local_dir, remote_dir):
        """Utility that calls `put` on every file in the specified directory
        copying them to the specified remote directory
        """
        file_list = os.listdir(local_dir)
        for file_name in file_list:
            local_path = os.path.join(local_dir, file_name)
            remote_path = os.path.join(remote_dir, file_name)
            self.put(local_path, remote_path)

    def mkdir(self, directory):
        """Create (recursively) directories emulating `mkdir -p`.
        Change `sftp` to this directory.
        Returns True if any folders were created
        """
        logger.info("Creating remote dir %s", directory)

        if directory == '/':
            # absolute path so change directory to root
            self.sftp.chdir('/')
            return
        if directory == '':
            # top-level relative directory must exist
            return
        try:
            self.sftp.chdir(directory)
        except IOError:
            # sub-directories do not exist
            dirname, basename = posixpath.split(directory.rstrip('/'))
            self.mkdir(dirname) # Make parent directories
            self.sftp.mkdir(basename)
            self.sftp.chdir(basename)
            return True
