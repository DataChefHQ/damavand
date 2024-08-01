from _pytest.monkeypatch import MonkeyPatch

from damavand import utils


def test_is_building(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("MODE", "BUILD")
    assert utils.is_building()

    monkeypatch.delenv("MODE")
    assert not utils.is_building()

    monkeypatch.setenv("MODE", "RUN")
    assert not utils.is_building()
