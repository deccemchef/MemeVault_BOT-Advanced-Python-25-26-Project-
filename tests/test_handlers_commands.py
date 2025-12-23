import pytest
from unittest.mock import AsyncMock


def test_commands_module_importable_and_has_router():
    from BOT.handlers import commands as c
    assert hasattr(c, "router")


@pytest.mark.asyncio
async def test_cmd_start_if_exposed(monkeypatch):
    from BOT.handlers import commands as c

    if not hasattr(c, "cmd_start"):
        pytest.skip("cmd_start не экспортируется как функция (только хендлер через router)")

    msg = type("M", (), {})()
    msg.from_user = type("U", (), {"id": 123, "username": "tester"})()
    msg.answer = AsyncMock()

    if hasattr(c, "rq"):
        if hasattr(c.rq, "ensure_user_exists"):
            monkeypatch.setattr(c.rq, "ensure_user_exists", AsyncMock(return_value=None), raising=False)

    await c.cmd_start(msg)
    msg.answer.assert_awaited()


@pytest.mark.asyncio
async def test_cmd_help_if_exposed():
    from BOT.handlers import commands as c

    if not hasattr(c, "cmd_help"):
        pytest.skip("cmd_help не экспортируется как функция (только хендлер через router)")

    msg = type("M", (), {"answer": AsyncMock()})()
    await c.cmd_help(msg)
    msg.answer.assert_awaited()
