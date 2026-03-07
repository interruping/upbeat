from __future__ import annotations

import pytest

from upbeat._config import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, Timeout, UpbeatConfig


class TestTimeout:
    def test_defaults(self) -> None:
        t = Timeout()
        assert t.connect == 10.0
        assert t.read == 30.0

    def test_custom_values(self) -> None:
        t = Timeout(connect=5.0, read=60.0)
        assert t.connect == 5.0
        assert t.read == 60.0

    def test_frozen_immutability(self) -> None:
        t = Timeout()
        with pytest.raises(AttributeError):
            t.connect = 99.0  # type: ignore[misc]


class TestUpbeatConfig:
    def test_defaults(self) -> None:
        config = UpbeatConfig()
        assert config.timeout == DEFAULT_TIMEOUT
        assert config.max_retries == DEFAULT_MAX_RETRIES
        assert config.auto_throttle is True

    def test_custom_values(self) -> None:
        custom_timeout = Timeout(connect=1.0, read=2.0)
        config = UpbeatConfig(
            timeout=custom_timeout, max_retries=5, auto_throttle=False
        )
        assert config.timeout.connect == 1.0
        assert config.max_retries == 5
        assert config.auto_throttle is False

    def test_partial_custom(self) -> None:
        config = UpbeatConfig(max_retries=10)
        assert config.timeout == DEFAULT_TIMEOUT
        assert config.max_retries == 10
        assert config.auto_throttle is True

    def test_frozen_immutability(self) -> None:
        config = UpbeatConfig()
        with pytest.raises(AttributeError):
            config.max_retries = 99  # type: ignore[misc]
