"""Tests for deterministic triage routing."""

import pytest

from src.services.agents.triage import (
    INTENT_PATTERNS,
    INTENT_TO_AGENT,
    TriageResult,
    classify_intent,
    get_agent_for_intent,
)


class TestTriageAgent:
    """Tests for the deterministic intent classifier."""

    @pytest.mark.parametrize(
        "message,expected",
        [
            ("What is a list comprehension in Python?", "concept-explanation"),
            ("Can you explain how decorators work?", "concept-explanation"),
            ("How does the garbage collector work?", "concept-explanation"),
            ("Define what a generator is", "concept-explanation"),
            ("What are Python modules?", "concept-explanation"),
            ("I am getting a TypeError in my code", "code-debug"),
            ("My code is not working, can you help?", "code-debug"),
            ("Traceback: IndexError: list index out of range", "code-debug"),
            ("How do I fix this bug?", "code-debug"),
            ("This function is broken, it gives wrong output", "code-debug"),
            ("Can you review my code?", "code-review"),
            ("How can I improve this function?", "code-review"),
            ("Is my code PEP 8 compliant?", "code-review"),
            ("Should I refactor this class?", "code-review"),
            ("Give me some practice exercises on loops", "exercise-generation"),
            ("I want a coding challenge on recursion", "exercise-generation"),
            ("Test me on dictionaries", "exercise-generation"),
            ("How am I doing in this course?", "progress-summary"),
            ("What is my mastery level in functions?", "progress-summary"),
            ("What is my current streak?", "progress-summary"),
            ("Hello, how are you?", "general"),
            ("Hi there!", "general"),
            ("WHAT IS A PYTHON LIST?", "concept-explanation"),
            ("I have an ERROR in my Code", "code-debug"),
        ],
    )
    def test_classify_intent(self, message, expected):
        result = classify_intent(message)
        assert result.intent == expected, f'"{message}" -> {result.intent} (expected {expected})'

    def test_confidence_capped_at_095(self):
        result = classify_intent(
            "What is explain how does what are what do define meaning of understand concept how do what does"
        )
        assert result.confidence <= 0.95

    def test_confidence_above_threshold(self):
        result = classify_intent("What is a Python list and how does it work?")
        assert result.confidence >= 0.08

    def test_matched_patterns_included(self):
        result = classify_intent("What is a list?")
        assert len(result.matched_patterns) > 0
        assert isinstance(result.matched_patterns[0], str)

    def test_no_matched_patterns_for_general(self):
        result = classify_intent("Hello world")
        assert result.matched_patterns == []
        assert result.confidence == 0.0

    @pytest.mark.parametrize(
        "intent,agent",
        [
            ("concept-explanation", "concepts"),
            ("code-debug", "debug"),
            ("code-review", "code_review"),
            ("exercise-generation", "exercise"),
            ("progress-summary", "progress"),
            ("general", "triage"),
        ],
    )
    def test_get_agent_for_intent(self, intent, agent):
        assert get_agent_for_intent(intent) == agent

    def test_get_agent_for_intent_unknown_defaults_triage(self):
        assert get_agent_for_intent("unknown-intent") == "triage"

    def test_triage_result_dataclass(self):
        result = TriageResult(intent="test", confidence=0.5, matched_patterns=["pattern1"])
        assert result.intent == "test"
        assert result.confidence == 0.5
        assert result.matched_patterns == ["pattern1"]

    def test_triage_result_default_matched_patterns(self):
        result = TriageResult(intent="test", confidence=0.5)
        assert result.matched_patterns == []

    def test_all_intent_categories_have_patterns(self):
        for intent in INTENT_PATTERNS:
            assert len(INTENT_PATTERNS[intent]) > 0

    def test_all_intents_mapped_to_agents(self):
        for intent in INTENT_PATTERNS:
            assert intent in INTENT_TO_AGENT
        assert "general" in INTENT_TO_AGENT
