import pytest

from datasciencebox.core.settings import Settings
from datasciencebox.core.cloud.cluster import Cluster

settings = Settings()


def test_cluster_from_to_list():
    data = [{'id': 0, 'ip': '0.0.0.0'}, {'id': 1, 'ip': '1.1.1.1'}, {'id': 2, 'ip': '2.2.2.2'}]
    cluster = Cluster.from_list(data, settings)

    exported = cluster.to_list()
    exported_ans = [{'id': 0,
                     'ip': '0.0.0.0'}, {'id': 1,
                                        'ip': '1.1.1.1'}, {'id': 2,
                                                           'ip': '2.2.2.2'}]

    assert isinstance(exported, list)
    assert exported == exported_ans
    assert len(cluster.instances) == 3
