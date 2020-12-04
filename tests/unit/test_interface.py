from ops.testing import Harness
from ops.charm import CharmBase

from k8s_service import ProvideK8sService, RequireK8sService


def test_provide():
    class ProvideCharm(CharmBase):
        def __init__(self, *args):
            super().__init__(*args)
            ProvideK8sService(
                self, "k8s-provides", service_name="service", service_port=666
            )

    harness = Harness(
        ProvideCharm,
        meta="""
        name: test-app
        provides:
            k8s-provides:
                interface: k8s-service
        """,
    )
    harness.set_leader(True)
    rel_id = harness.add_relation("k8s-provides", "test-app")
    harness.begin()
    rel_data = harness.get_relation_data(rel_id, "test-app")
    assert rel_data["service-name"] == "service"
    assert rel_data["service-port"] == "666"


class RequireCharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.k8s_service = RequireK8sService(self, "k8s-requires")


def test_require():
    harness = Harness(
        RequireCharm,
        meta="""
        name: test-app
        requires:
            k8s-requires:
                interface: k8s-service
        """,
    )
    harness.set_leader(True)
    rel_id = harness.add_relation("k8s-requires", "test-app2")
    harness.begin()
    assert harness.charm.k8s_service.is_created
    assert not harness.charm.k8s_service.is_available
    harness.add_relation_unit(rel_id, "test-app2/0")
    harness.update_relation_data(
        rel_id, "test-app2", {"service-name": "service", "service-port": "666"}
    )
    assert harness.charm.k8s_service.is_available

    service_name, service_port = harness.charm.k8s_service.services[0]
    assert service_name == "service" and service_port == "666"


def test_require_no_relation():
    harness = Harness(
        RequireCharm,
        meta="""
        name: test-app
        requires:
            k8s-requires:
                interface: k8s-service
        """,
    )
    harness.set_leader(True)
    harness.begin()
    assert not harness.charm.k8s_service.is_created
    assert not harness.charm.k8s_service.is_available
