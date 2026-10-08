"""OWNER: P4. Proves evora.chat / evora.memory honor the contract, incl. clarify-once."""
from evora.chat import Engine, parse
from evora.core.schemas import Location, QuerySpec
from evora.memory import Memory, normalize_alias

Q = "Did a red car pass through the main gate in the last hour?"


def test_normalize_alias():
    assert normalize_alias("The Main Gate") == normalize_alias("main gate")


def test_parse_marks_unknown_alias_unresolved():
    spec = parse(Q, Memory())
    assert isinstance(spec, QuerySpec)
    assert "main gate" in spec.unresolved


def test_parse_uses_memory():
    m = Memory()
    loc = m.learn("main gate", "cam01")
    assert isinstance(loc, Location)
    spec = parse(Q, m)
    assert spec.unresolved == [] and spec.camera_ids == ["cam01"]


def test_clarify_once_flow():
    eng = Engine(memory=Memory())
    a1 = eng.ask(Q)
    assert a1.kind == "clarify" and a1.clarify_alias == "main gate"
    a2 = eng.clarify("main gate", "cam01")
    assert a2.kind == "answer" and a2.hits and a2.hits[0].camera_id == "cam01"
    a3 = eng.ask(Q)                      # must NOT ask again
    assert a3.kind != "clarify"
