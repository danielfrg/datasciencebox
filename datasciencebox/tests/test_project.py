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
