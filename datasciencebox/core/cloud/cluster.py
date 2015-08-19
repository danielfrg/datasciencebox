import os
import warnings

from libcloud.compute.base import NodeImage

from datasciencebox.core.logger import getLogger
logger = getLogger()
from datasciencebox.core.cloud.driver import Driver
from datasciencebox.core.cloud.instance import Instance
from datasciencebox.core.exceptions import DSBException, DSBWarning


class Cluster(object):

    def __init__(self, driver=None, settings=None):
        logger.debug('Initializing Cluster')
        self._driver = driver
        self.settings = settings
        self.instances = []

    @classmethod
    def from_list(cls, values, settings):
        """
        From a list of dicts (each dict is an instances)
        """
        logger.debug('Creating Cluster from list')
        self = cls()
        self.settings = settings
        self.instances = []

        for instance in values:
            new_instance = Instance.from_dict(instance, settings, cluster=self)
            self.instances.append(new_instance)
        return self

    def to_list(self):
        """
        To a list of dicts (each dict is an instances)
        """
        ret = []
        for instance in self.instances:
            ret.append(instance.to_dict())
        return ret

    def __len__(self):
        return len(self.instances)

    @property
    def master(self):
        return self.instances[0]

    @property
    def driver(self):
        if self._driver is None:
            self._driver = Driver.new(self.settings)
        return self._driver

    def get_driver(self):
        if self._driver is None:
            self._driver = Driver.new(self.settings)
        return self._driver

    def set_driver(self, value):
        self._uid = value

    driver = property(get_driver, set_driver, None)

    def create(self):
        if self.settings['CLOUD'] == 'bare':
            warnings.warn("Bare Metal cluster cannot be created", DSBWarning)
            return

        instances = []
        for i in range(self.settings['NUMBER_NODES']):
            new_instance = Instance.new(settings=self.settings, driver=self.driver)
            instances.append(new_instance)

        create_nodes = [instance.create(suffix=i) for i, instance in enumerate(instances)]
        fetch_nodes = [instance.node for instance in instances]
        self.driver.wait_until_running(fetch_nodes)

        node_ids = [node.id for node in fetch_nodes]
        all_nodes = self.driver.list_nodes()
        new_nodes = [node for node in all_nodes if node.id in node_ids]
        for instance, node in zip(instances, new_nodes):
            instance.node = node
        self.instances = instances

    def fetch_nodes(self):
        for instance in self.instances:
            instance.driver = self.driver
            instance.fetch_node()

    def destroy(self):
        for instance in self.instances:
            instance.destroy()
