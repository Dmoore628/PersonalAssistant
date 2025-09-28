# Simple smoke test for health schema
from archi_core import Health, PlanMessage


def test_health_schema():
    h = Health(service="x", status="ok")
    assert h.service == "x"
    assert h.status == "ok"


def test_planmessage_roundtrip():
    p = PlanMessage(
        id="123", title="T", description=None, priority=3, tags=["a"], source="planning"
    )
    s = p.model_dump_json()
    p2 = PlanMessage.model_validate_json(s)
    assert p2.id == p.id
    assert p2.title == p.title
    assert p2.tags == p.tags
