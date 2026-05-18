from __future__ import annotations

import json
import logging

from app.core import logging as log_module


def test_configure_logging_emits_json(capsys):
    log_module.configure_logging("INFO")
    logger = log_module.get_logger("test.logger")
    logger.info("hello", extra={"event": "test", "value": 42})

    captured = capsys.readouterr().out.strip().splitlines()
    payload = json.loads(captured[-1])
    assert payload["level"] == "INFO"
    assert payload["logger"] == "test.logger"
    assert payload["message"] == "hello"
    assert payload["event"] == "test"
    assert payload["value"] == 42
    assert "timestamp" in payload


def test_exception_formatting(capsys):
    log_module.configure_logging("INFO")
    logger = log_module.get_logger("test.exc")
    try:
        raise ValueError("boom")
    except ValueError:
        logger.exception("caught")
    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert "ValueError: boom" in payload["exception"]


def test_configure_replaces_existing_handlers():
    log_module.configure_logging("DEBUG")
    handlers_first = list(logging.getLogger().handlers)
    log_module.configure_logging("DEBUG")
    handlers_second = list(logging.getLogger().handlers)
    assert len(handlers_second) == 1
    assert handlers_first != handlers_second  # replaced, not appended
