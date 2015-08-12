import pytest

from datasciencebox.core.project import Project
from datasciencebox.core.settings import Settings
from datasciencebox.core.cloud.cluster import Cluster


settings = Settings()
settings['USERNAME'] = 'me'
settings['KEYPAIR'] = '~/.ssh/id_rsa'

_ = [{'id': 0, 'ip': '0.0.0.0'}, {'id': 1, 'ip': '1.1.1.1'}, {'id': 2, 'ip': '2.2.2.2'}]
cluster = Cluster.from_list(_, settings)

project = Project()
project.settings = settings
project.cluster = cluster

def test_generate_roster():
    roster = project.generate_roster()
    ans = { 'master': {'host': '0.0.0.0', 'sudo': True, 'user': 'me', 'priv': '~/.ssh/id_rsa'},
            'minion-1': {'host': '1.1.1.1', 'sudo': True, 'user': 'me', 'priv': '~/.ssh/id_rsa'},
            'minion-2': {'host': '2.2.2.2', 'sudo': True, 'user': 'me', 'priv': '~/.ssh/id_rsa'}
        }
    assert roster == ans
