import pytest

from datasciencebox.core.settings import Settings
from datasciencebox.core.cloud.cluster import Cluster
from datasciencebox.core.cloud.instance import Instance, BareInstance, AWSInstance, GCPInstance

settings = Settings()


def test_cluster_from_to_list():
    input_dict = [{'id': 0,
                   'ip': '0.0.0.0'}, {'id': 1,
                                      'ip': '1.1.1.1'}, {'id': 2,
                                                         'ip': '2.2.2.2'}]
    cluster = Cluster.from_list(input_dict, settings)

    exported = cluster.to_list()
    assert isinstance(exported, list)
    assert exported == input_dict
    assert len(cluster.instances) == 3

    for i, instance in enumerate(cluster.instances):
        assert isinstance(instance, BareInstance)
        assert cluster.instances[i].uid == i
        assert cluster.instances[i].ip == '{0}.{0}.{0}.{0}'.format(i)
