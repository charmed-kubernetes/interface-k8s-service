from ops.framework import Object, StoredState, EventBase, EventSource, ObjectEvents
from operator import attrgetter
from hashlib import md5
import logging


class K8sServiceAvailable(EventBase):
    pass


class RequireK8sServiceEvents(ObjectEvents):
    k8s_service_available = EventSource(K8sServiceAvailable)


class ProvideK8sService(Object):
    def __init__(self, charm, relation_name, service_name, service_port):
        super().__init__(charm, relation_name)
        for relation in self.model.relations[relation_name]:
            relation.data[charm.app].update({
                "service-name": service_name,
                "service-port": str(service_port),
            })


class RequireK8sService(Object):
    state = StoredState()
    on = RequireK8sServiceEvents()

    def __init__(self, charm, relation_name):
        super().__init__(charm, relation_name)
        self.state.set_default(data_hash=None)

        self.services = []
        for relation in sorted(self.model.relations[relation_name], key=attrgetter('id')):
            if not relation.app:
                continue
            service_name = relation.data[relation.app].get("service-name")
            service_port = relation.data[relation.app].get("service-port")
            if service_name and service_port:
                self.services.append((service_name, service_port))

        self.is_available = bool(self.services)
        self.is_created = bool(self.model.relations[relation_name])

        data_hash = md5(str(self.services).encode('utf8')).hexdigest()
        if self.is_available and self.state.data_hash != data_hash:
            self.state.data_hash = data_hash
            self.on.k8s_service_available.emit()
