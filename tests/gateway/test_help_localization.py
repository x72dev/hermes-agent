from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from gateway.config import Platform
from gateway.platforms.base import MessageEvent
from gateway.session import SessionSource


def _make_event(platform: Platform) -> MessageEvent:
    source = SessionSource(
        platform=platform,
        user_id="u1",
        chat_id="c1",
        user_name="tester",
        chat_type="dm",
    )
    return MessageEvent(text="/help", source=source, message_id="m1")


def _make_runner():
    from gateway.run import GatewayRunner

    runner = object.__new__(GatewayRunner)
    runner.adapters = {}
    runner.hooks = SimpleNamespace(emit=AsyncMock(), loaded_hooks=False)
    return runner


@pytest.mark.asyncio
async def test_help_command_is_chinese_on_telegram(monkeypatch):
    runner = _make_runner()

    fake_skill_cmds = {
        "/plan": {"description": "Plan work before coding"},
    }

    import agent.skill_commands as skill_commands

    monkeypatch.setattr(skill_commands, "get_skill_commands", lambda: fake_skill_cmds)

    result = await runner._handle_help_command(_make_event(Platform.TELEGRAM))

    assert "Hermes 命令" in result
    assert "显示可用命令" in result
    assert "技能命令" in result
    assert "已启用" in result
    assert "`/plan` — Plan work before coding" in result


@pytest.mark.asyncio
async def test_commands_command_is_chinese_on_telegram(monkeypatch):
    runner = _make_runner()

    fake_skill_cmds = {
        "/plan": {"description": "Plan work before coding"},
    }

    import agent.skill_commands as skill_commands

    monkeypatch.setattr(skill_commands, "get_skill_commands", lambda: fake_skill_cmds)

    event = _make_event(Platform.TELEGRAM)
    event.text = "/commands 3"
    result = await runner._handle_commands_command(event)

    assert "命令列表" in result
    assert "技能命令" in result
    assert "`/plan` — Plan work before coding" in result
    assert "Skill Commands" not in result


@pytest.mark.asyncio
async def test_help_command_stays_english_off_telegram(monkeypatch):
    runner = _make_runner()

    import agent.skill_commands as skill_commands

    monkeypatch.setattr(skill_commands, "get_skill_commands", lambda: {})

    result = await runner._handle_help_command(_make_event(Platform.DISCORD))

    assert "Hermes Commands" in result
    assert "Show available commands" in result
