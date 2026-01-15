"""Tests for prompts module."""

import pytest

from config.prompts import (
    load_prompt,
    get_all_prompts,
    get_agent_names,
    prompt_exists,
    AGENT_PROMPTS,
    AGENT_ALIASES,
)


class TestLoadPrompt:
    """Tests for load_prompt function."""
    
    def test_load_prompt_full_name(self) -> None:
        """Test loading prompt by full agent name."""
        prompt = load_prompt("Evaluador_FEI")
        
        assert prompt is not None
        assert len(prompt) > 0
        assert "FEI" in prompt  # Should mention FEI
    
    def test_load_prompt_alias(self) -> None:
        """Test loading prompt by alias."""
        prompt = load_prompt("evaluador_fei")
        
        assert prompt is not None
        assert "FEI" in prompt
    
    def test_load_prompt_short_alias(self) -> None:
        """Test loading prompt by short alias."""
        prompt = load_prompt("evaluador")
        
        assert prompt is not None
        assert "FEI" in prompt
    
    def test_load_prompt_all_agents(self) -> None:
        """Test that all agents have valid prompts."""
        for agent_name in AGENT_PROMPTS:
            prompt = load_prompt(agent_name)
            assert prompt is not None
            assert len(prompt) > 100  # Should have substantial content
    
    def test_load_prompt_unknown_agent(self) -> None:
        """Test error for unknown agent."""
        with pytest.raises(ValueError) as exc_info:
            load_prompt("UnknownAgent")
        
        assert "Unknown agent" in str(exc_info.value)
    
    def test_load_prompt_case_insensitive(self) -> None:
        """Test that aliases are case insensitive."""
        prompt1 = load_prompt("EVALUADOR_FEI")
        prompt2 = load_prompt("evaluador_fei")
        
        assert prompt1 == prompt2


class TestPromptContent:
    """Tests for prompt content quality."""
    
    def test_buscador_prompt_contains_required_sections(self) -> None:
        """Test Buscador prompt has required sections."""
        prompt = load_prompt("buscador")
        
        assert "# Agente: Buscador_Empresas" in prompt
        assert "## Rol" in prompt
        assert "## Objetivo" in prompt
        assert "## Criterios" in prompt or "## Criterios de Búsqueda" in prompt
    
    def test_enriquecedor_prompt_contains_required_sections(self) -> None:
        """Test Enriquecedor prompt has required sections."""
        prompt = load_prompt("enriquecedor")
        
        assert "# Agente: Enriquecedor_Datos" in prompt
        assert "## Rol" in prompt
        assert "## Datos a Extraer" in prompt
    
    def test_evaluador_fei_prompt_contains_criteria(self) -> None:
        """Test Evaluador FEI prompt contains all 6 criteria."""
        prompt = load_prompt("evaluador_fei")
        
        assert "1.1_Cleantech_Prize" in prompt
        assert "1.2_Clean_Energy_Patent" in prompt
        assert "1.3_Eco_Label" in prompt
        assert "1.4_Green_Business_90" in prompt
        assert "1.5_Green_Business_Model" in prompt
        assert "1.6_Environmental_Certificate" in prompt
    
    def test_selector_prompt_contains_rules(self) -> None:
        """Test Selector prompt contains business rules."""
        prompt = load_prompt("selector")
        
        assert "cooling-off" in prompt.lower() or "cooling_off" in prompt.lower()
        assert "90" in prompt  # 90 days cooling off
        assert "30" in prompt  # Max 30 targets
        assert "Fit Score" in prompt or "fit_score" in prompt
    
    def test_redactor_prompt_contains_word_limit(self) -> None:
        """Test Redactor prompt mentions 150 word limit."""
        prompt = load_prompt("redactor")
        
        assert "150" in prompt
        assert "palabras" in prompt.lower() or "words" in prompt.lower()


class TestGetAllPrompts:
    """Tests for get_all_prompts function."""
    
    def test_get_all_prompts_returns_all(self) -> None:
        """Test get_all_prompts returns all 6 agent prompts."""
        prompts = get_all_prompts()
        
        assert len(prompts) == 6
        assert "Buscador_Empresas" in prompts
        assert "Enriquecedor_Datos" in prompts
        assert "Evaluador_FEI" in prompts
        assert "Analizador_Contexto" in prompts
        assert "Selector_Targets" in prompts
        assert "Redactor_Mensajes" in prompts
    
    def test_get_all_prompts_values_not_empty(self) -> None:
        """Test all prompts have content."""
        prompts = get_all_prompts()
        
        for agent, prompt in prompts.items():
            assert len(prompt) > 0, f"Prompt for {agent} is empty"


class TestGetAgentNames:
    """Tests for get_agent_names function."""
    
    def test_get_agent_names_returns_all(self) -> None:
        """Test get_agent_names returns all 6 agents."""
        names = get_agent_names()
        
        assert len(names) == 6
        assert "Buscador_Empresas" in names
        assert "Redactor_Mensajes" in names


class TestPromptExists:
    """Tests for prompt_exists function."""
    
    def test_prompt_exists_true(self) -> None:
        """Test prompt_exists returns True for valid agents."""
        assert prompt_exists("Evaluador_FEI") is True
        assert prompt_exists("evaluador_fei") is True
        assert prompt_exists("evaluador") is True
    
    def test_prompt_exists_false(self) -> None:
        """Test prompt_exists returns False for invalid agents."""
        assert prompt_exists("UnknownAgent") is False
        assert prompt_exists("") is False


class TestAgentMappings:
    """Tests for agent name mappings."""
    
    def test_all_prompts_have_files(self) -> None:
        """Test all mapped prompts have corresponding files."""
        for agent_name in AGENT_PROMPTS:
            assert prompt_exists(agent_name)
    
    def test_all_aliases_resolve(self) -> None:
        """Test all aliases resolve to valid full names."""
        for alias, full_name in AGENT_ALIASES.items():
            assert full_name in AGENT_PROMPTS
            assert prompt_exists(alias)

