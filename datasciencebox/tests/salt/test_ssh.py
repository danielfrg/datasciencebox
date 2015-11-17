from __future__ import unicode_literals

import pytest

from ..salt import utils


# @utils.remotetest
# def test_echo_user():
#     project = utils.get_test_project()
#     node = project.cluster.head
#     client = node.ssh_client

#     output = client.exec_command('echo $USER')
#     assert output['exit_code'] == 0
#     assert output['stdout'].strip() == node.username


# @utils.remotetest
# def test_mkdir():
#     import math
#     import random
#
#     project = utils.get_test_project()
#     node = project.cluster.head
#     client = node.ssh_client
#
#     dir_name = '/tmp/{}.txt'.format(unicode(int(math.floor(random.random() * 1000))))
#     output = client.exec_command('test -d %s' % dir_name)
#     print(output)
#     assert output['exit_code'] == 1
#
#     client.mkdir(dir_name)
#     output = client.exec_command('test -d %s' % dir_name)
#     print(output)
#     assert output['exit_code'] == 0


# @utils.remotetest
# def test_put_file(tmpdir):
#     import math
#     import random
#
#     project = utils.get_test_project()
#     node = project.cluster.head
#     client = node.ssh_client
#
#     file_name = '{}.txt'.format(unicode(int(math.floor(random.random() * 1000))))
#     content = unicode(int(math.floor(random.random() * 100000000)))
#     tfile = tmpdir.join(file_name)
#     tfile.write(content)
#
#     local = tfile.realpath().strpath
#     remote = '/tmp/{}'.format(file_name)
#
#     client.put(local, remote)
#
#     output = client.exec_command('test -e %s' % remote)
#     assert output['exit_code'] == 0
#
#     output = client.exec_command('cat %s' % remote)
#     assert output['stdout'] == content


@utils.remotetest
def test_put_dir(tmpdir):
    """
    Copy a directory to the remote node

    Tries to emulate a basic salt structure
    """
    import math
    import random
    import posixpath

    project = utils.get_test_project()
    node = project.cluster.head
    client = node.ssh_client

    # Create tmp files to upload
    rnd = '{}'.format(int(math.floor(random.random() * 1000)))
    root_tdir = tmpdir.mkdir(rnd)
    salt = root_tdir.mkdir('salt')
    mesos = salt.mkdir('mesos')
    m_init = mesos.join('init.sls')
    m_init.write('mesos/init.sls')
    conda = salt.mkdir('conda')
    c_init = conda.join('init.sls')
    c_init.write('conda/init.sls')
    c_settings = conda.join('settings.sls')
    c_settings.write('conda/settings.sls')

    local = root_tdir.realpath().strpath
    remote = '/tmp/{}'.format(rnd)

    client.put(local, remote)

    output = client.exec_command('test -d %s' % remote)
    assert output['exit_code'] == 0

    file_ = posixpath.join(remote, 'salt')
    output = client.exec_command('test -d %s' % file_)
    assert output['exit_code'] == 0

    file_ = posixpath.join(remote, 'salt', 'mesos')
    output = client.exec_command('test -d %s' % file_)
    assert output['exit_code'] == 0

    file_ = posixpath.join(remote, 'salt', 'mesos', 'init.sls')
    output = client.exec_command('test -e %s' % file_)
    assert output['exit_code'] == 0

    file_ = posixpath.join(remote, 'salt', 'conda')
    output = client.exec_command('test -d %s' % file_)
    assert output['exit_code'] == 0

    file_ = posixpath.join(remote, 'salt', 'conda', 'init.sls')
    output = client.exec_command('test -e %s' % file_)
    assert output['exit_code'] == 0

    file_ = posixpath.join(remote, 'salt', 'conda', 'settings.sls')
    output = client.exec_command('test -e %s' % file_)
    assert output['exit_code'] == 0
