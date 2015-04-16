import pytest

from datasciencebox.core.cloud import Cluster, Instance, BareInstance, AWSInstance
from datasciencebox.core.dsbfile import DSBFile


dsbfile = DSBFile()


def test_instance_bare():
    ins = Instance.new(dsbfile)
    assert type(ins) == BareInstance

    ins = Instance.new(dsbfile, info={'id': '123', 'ip': '1.2.3.4'})
    assert ins.ip == '1.2.3.4'
    assert ins.uid == '123'


def test_instance_aws():
    dsbfile = DSBFile()
    dsbfile['cloud'] = 'aws'

    ins = Instance.new(dsbfile)
    assert type(ins) == AWSInstance


def test_cluster_from_to_list():
    data = [{'id': 0, 'ip': '0.0.0.0'}, {'id': 1, 'ip': '1.1.1.1'}, {'id': 2, 'ip': '2.2.2.2'}]
    cluster = Cluster.from_list(data, dsbfile)

    exported = cluster.to_list()
    assert type(exported) == list
    assert data == exported
    assert len(cluster.instances) == 3
