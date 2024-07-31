from _pytest.monkeypatch import MonkeyPatch

from damavand.resource import buildtime, runtime


def test_buildtime_decorator(monkeypatch: MonkeyPatch):
    @buildtime
    def test_func(_):
        return "building"

    monkeypatch.setattr("damavand.utils.is_building", lambda: True)
    assert test_func(None) == "building"

    monkeypatch.setattr("damavand.utils.is_building", lambda: False)
    assert test_func(None) is None


def test_runtime_decorator(monkeypatch: MonkeyPatch):
    @runtime
    def test_func(_):
        return "running"

    monkeypatch.setattr("damavand.utils.is_building", lambda: True)
    assert test_func(None) is None

    monkeypatch.setattr("damavand.utils.is_building", lambda: False)
    assert test_func(None) == "running"
