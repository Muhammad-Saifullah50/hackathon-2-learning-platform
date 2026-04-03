"""Tests for SDK-based agent definitions."""

import uuid

import pytest

from src.services.agents.agents import (
    get_code_review_agent,
    get_concepts_agent,
    get_debug_agent,
    get_exercise_agent,
    get_progress_agent,
    get_triage_agent,
)
from src.services.agents.context import LearnFlowContext


class TestLearnFlowContext:
    """Tests for the SDK context object."""

    def test_minimal_context(self):
        user_id = uuid.uuid4()
        ctx = LearnFlowContext(user_id=user_id)
        assert ctx.user_id == user_id
        assert ctx.session_id is None
        assert ctx.db is None
        assert ctx.topic is None
        assert ctx.code_snippet is None
        assert ctx.level is None
        assert ctx.intent is None

    def test_full_context(self):
        user_id = uuid.uuid4()
        session_id = uuid.uuid4()
        ctx = LearnFlowContext(
            user_id=user_id,
            session_id=session_id,
            topic="loops",
            code_snippet="for i in range(10): pass",
            level="beginner",
            intent="concept-explanation",
            extra={"key": "value"},
        )
        assert ctx.session_id == session_id
        assert ctx.topic == "loops"
        assert ctx.level == "beginner"
        assert ctx.extra == {"key": "value"}


class TestSDKAgentDefinitions:
    """Tests that SDK agents are properly defined."""

    def test_triage_agent_has_handoffs(self):
        agent = get_triage_agent()
        assert agent.name == "triage"
        assert agent.handoffs is not None
        assert len(agent.handoffs) == 5

    def test_concepts_agent_has_dynamic_instructions(self):
        agent = get_concepts_agent()
        assert agent.name == "concepts"
        assert callable(agent.instructions)

    def test_debug_agent_has_dynamic_instructions(self):
        agent = get_debug_agent()
        assert agent.name == "debug"
        assert callable(agent.instructions)

    def test_code_review_agent_has_tools(self):
        agent = get_code_review_agent()
        assert agent.name == "code_review"
        assert agent.tools is not None
        assert len(agent.tools) >= 1

    def test_exercise_agent_has_tools(self):
        agent = get_exercise_agent()
        assert agent.name == "exercise"
        assert agent.tools is not None
        assert len(agent.tools) >= 1

    def test_progress_agent_has_tools(self):
        agent = get_progress_agent()
        assert agent.name == "progress"
        assert agent.tools is not None
        assert len(agent.tools) >= 1

    def test_all_agents_have_model_settings(self):
        agents = [
            get_triage_agent(),
            get_concepts_agent(),
            get_debug_agent(),
            get_code_review_agent(),
            get_exercise_agent(),
            get_progress_agent(),
        ]
        for agent in agents:
            assert agent.model_settings is not None
