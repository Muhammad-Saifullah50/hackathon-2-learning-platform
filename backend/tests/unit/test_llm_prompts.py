"""Unit tests for LLM prompt constants."""

from src.llm.prompts import (
    get_code_review_agent_prompt,
    get_concept_agent_prompt,
    get_debug_agent_prompt,
    get_exercise_agent_prompt,
    get_progress_agent_prompt,
    get_triage_agent_prompt,
)


class TestPromptFunctions:
    """Tests for agent prompt functions."""

    def test_concept_agent_prompt_not_empty(self):
        prompt = get_concept_agent_prompt()
        assert len(prompt) > 0
        assert "Python" in prompt or "tutor" in prompt.lower()

    def test_code_review_agent_prompt_not_empty(self):
        prompt = get_code_review_agent_prompt()
        assert len(prompt) > 0
        assert "code" in prompt.lower()

    def test_debug_agent_prompt_not_empty(self):
        prompt = get_debug_agent_prompt()
        assert len(prompt) > 0
        assert "debug" in prompt.lower() or "error" in prompt.lower()

    def test_exercise_agent_prompt_not_empty(self):
        prompt = get_exercise_agent_prompt()
        assert len(prompt) > 0
        assert "exercise" in prompt.lower() or "challenge" in prompt.lower()

    def test_triage_agent_prompt_not_empty(self):
        prompt = get_triage_agent_prompt()
        assert len(prompt) > 0
        assert "route" in prompt.lower() or "triage" in prompt.lower()

    def test_progress_agent_prompt_not_empty(self):
        prompt = get_progress_agent_prompt()
        assert len(prompt) > 0
        assert "progress" in prompt.lower()

    def test_prompts_are_distinct(self):
        prompts = [
            get_concept_agent_prompt(),
            get_code_review_agent_prompt(),
            get_debug_agent_prompt(),
            get_exercise_agent_prompt(),
            get_triage_agent_prompt(),
            get_progress_agent_prompt(),
        ]
        unique_prompts = set(prompts)
        assert len(unique_prompts) == len(prompts), "All agent prompts should be distinct"
