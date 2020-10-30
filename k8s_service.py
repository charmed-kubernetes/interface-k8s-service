from ops.framework import Object, StoredState, EventBase, EventSource, ObjectEvents


class K8sServiceAvailable(EventBase):
    pass


class RequireK8sServiceEvents(ObjectEvents):
    k8s_service_available = EventSource(K8sServiceAvailable)


class ProvideK8sService(Object):
    def __init__(self, charm, relation_name):
        super().__init__(charm, relation_name)
        self._relation_name = relation_name

        self.framework.observe(
            charm.on[relation_name].relation_joined, self._on_relation_joined
        )

        self.charm = charm
    
    def _on_relation_joined(self, event):
        service_data = event.relation.data[self.charm.app]

        service_data.update({
            'service-name': self.framework.model.app.name,
            'service-port': str(self.charm.model.config["port"]),
        })


class RequireK8sService(Object):
    state = StoredState()
    on = RequireK8sServiceEvents()

    def __init__(self, charm, relation_name):
        super().__init__(charm, relation_name)
        self._relation_name = relation_name

        self.framework.observe(
            charm.on[relation_name].relation_changed, self._on_relation_changed
        )

        self.charm = charm
        self.state.set_default(is_available=False)
        self.state.set_default(service_port=None)
        self.state.set_default(service_name=None)

    def _on_relation_changed(self, event):
        service_data = event.relation.data[event.app]

        if not service_data.get("service-name"):
            return

        self.state.is_available = True
        self.state.service_name = service_data.get("service-name")
        self.state.service_port = service_data.get("service-port")
        self.on.k8s_service_available.emit()

    def is_available(self):
        return self.state.is_available

    @property
    def service_name(self):
        return self.state.service_name

    @property
    def service_port(self):
        return self.state.service_port
