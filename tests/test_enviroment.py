from _pytest.monkeypatch import MonkeyPatch
from damavand.environment import Environment


def test_from_system_env(monkeypatch: MonkeyPatch) -> None:
    """Test the `from_system_env` method."""

    monkeypatch.setenv("ENVIRONMENT", "production")
    assert Environment.from_system_env() == Environment.PRODUCTION

    monkeypatch.setenv("ENVIRONMENT", "development")
    assert Environment.from_system_env() == Environment.DEVELOPMENT

    monkeypatch.setenv("ENVIRONMENT", "testing")
    assert Environment.from_system_env() == Environment.TESTING

    monkeypatch.setenv("ENVIRONMENT", "acceptance")
    assert Environment.from_system_env() == Environment.ACCEPTANCE

    monkeypatch.setenv("ENVIRONMENT", "local")
    assert Environment.from_system_env() == Environment.LOCAL

    monkeypatch.delenv("ENVIRONMENT")
    assert Environment.from_system_env() == Environment.LOCAL


def test_all() -> None:
    """Test the `all` method."""

    assert Environment.all() == [
        Environment.PRODUCTION,
        Environment.DEVELOPMENT,
        Environment.TESTING,
        Environment.ACCEPTANCE,
        Environment.LOCAL,
    ]


def test_all_values() -> None:
    """Test the `all_values` method."""

    assert Environment.all_values() == [
        "production",
        "development",
        "testing",
        "acceptance",
        "local",
    ]
