"""Tests for agent schemas."""

import pytest
from pydantic import ValidationError

from src.schemas.agents import (
    AgentChatRequest,
    ExerciseGenerationRequest,
    ExerciseSubmissionRequest,
    HintAdvanceRequest,
    HintResponse,
    ProgressSummaryResponse,
    StreakInfo,
    TestCase,
    TestResult,
    TopicMastery,
)


class TestAgentChatRequest:
    def test_valid_request(self):
        req = AgentChatRequest(message="What is a list?")
        assert req.message == "What is a list?"
        assert req.topic is None

    def test_with_all_fields(self):
        req = AgentChatRequest(
            message="Fix this code",
            topic="loops",
            session_id="abc-123",
            code_snippet="for i in range(10): print(i)",
        )
        assert req.message == "Fix this code"
        assert req.code_snippet == "for i in range(10): print(i)"

    def test_empty_message_raises(self):
        with pytest.raises(ValidationError):
            AgentChatRequest(message="")


class TestExerciseGenerationRequest:
    def test_valid_request(self):
        req = ExerciseGenerationRequest(topic="loops", difficulty="beginner")
        assert req.difficulty == "beginner"

    def test_invalid_difficulty_raises(self):
        with pytest.raises(ValidationError):
            ExerciseGenerationRequest(topic="test", difficulty="expert")


class TestExerciseSubmissionRequest:
    def test_valid_request(self):
        req = ExerciseSubmissionRequest(code="print('hello')")
        assert req.code == "print('hello')"

    def test_empty_code_raises(self):
        with pytest.raises(ValidationError):
            ExerciseSubmissionRequest(code="")


class TestHintAdvanceRequest:
    def test_default_request_solution(self):
        req = HintAdvanceRequest(session_id="abc-123")
        assert req.request_solution is False


class TestProgressSummaryResponse:
    def test_with_streak(self):
        resp = ProgressSummaryResponse(
            overall_mastery=75.0,
            topics=[],
            weak_areas=[],
            streak=StreakInfo(current_streak=5, longest_streak=10),
            recommendations=["Keep going!"],
            missing_components=[],
        )
        assert resp.streak.current_streak == 5


class TestTopicMastery:
    def test_valid(self):
        tm = TopicMastery(
            topic="loops",
            score=85.0,
            level="Proficient",
            component_breakdown={"exercises": 90},
        )
        assert tm.score == 85.0


class TestTestResult:
    def test_passed(self):
        tr = TestResult(test_index=0, passed=True)
        assert tr.passed is True
        assert tr.error_message is None

    def test_failed(self):
        tr = TestResult(test_index=1, passed=False, error_message="Expected 5, got 3")
        assert tr.passed is False
