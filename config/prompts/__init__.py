"""Prompts module for Alter-5 Origination Engine agents.

This module provides functions to load system prompts from markdown files
for each AI agent. Prompts are stored as .md files for easy editing and
version control.

Usage:
    from config.prompts import load_prompt, get_all_prompts
    
    # Load a specific agent's prompt
    prompt = load_prompt("evaluador_fei")
    
    # Load all prompts
    prompts = get_all_prompts()
"""

from pathlib import Path
from typing import Optional
import structlog

logger = structlog.get_logger()

# Path to prompts directory
PROMPTS_DIR = Path(__file__).parent

# Agent name to filename mapping
AGENT_PROMPTS = {
    "Buscador_Empresas": "buscador.md",
    "Enriquecedor_Datos": "enriquecedor.md",
    "Evaluador_FEI": "evaluador_fei.md",
    "Analizador_Contexto": "analizador.md",
    "Selector_Targets": "selector.md",
    "Redactor_Mensajes": "redactor.md",
}

# Short aliases for convenience
AGENT_ALIASES = {
    "buscador": "Buscador_Empresas",
    "enriquecedor": "Enriquecedor_Datos",
    "evaluador_fei": "Evaluador_FEI",
    "evaluador": "Evaluador_FEI",
    "analizador": "Analizador_Contexto",
    "selector": "Selector_Targets",
    "redactor": "Redactor_Mensajes",
}


def load_prompt(agent_name: str) -> str:
    """Load the system prompt for an agent.
    
    Args:
        agent_name: Agent name (full or alias). Examples:
            - "Evaluador_FEI" (full name)
            - "evaluador_fei" (alias)
            - "evaluador" (short alias)
            
    Returns:
        The prompt content as a string
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist
        ValueError: If the agent name is not recognized
    """
    # Resolve alias to full name
    normalized = agent_name.lower().replace("-", "_")
    if normalized in AGENT_ALIASES:
        full_name = AGENT_ALIASES[normalized]
    elif agent_name in AGENT_PROMPTS:
        full_name = agent_name
    else:
        raise ValueError(
            f"Unknown agent: {agent_name}. "
            f"Valid agents: {list(AGENT_PROMPTS.keys())}"
        )
    
    # Get filename
    filename = AGENT_PROMPTS[full_name]
    filepath = PROMPTS_DIR / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    
    content = filepath.read_text(encoding="utf-8")
    
    logger.debug(
        "prompt_loaded",
        agent=full_name,
        file=filename,
        length=len(content),
    )
    
    return content


def get_all_prompts() -> dict[str, str]:
    """Load all agent prompts.
    
    Returns:
        Dict mapping agent names to their prompts
    """
    prompts = {}
    for agent_name in AGENT_PROMPTS:
        try:
            prompts[agent_name] = load_prompt(agent_name)
        except FileNotFoundError:
            logger.warning(f"Prompt file missing for agent: {agent_name}")
    
    return prompts


def get_agent_names() -> list[str]:
    """Get list of all agent names.
    
    Returns:
        List of agent names
    """
    return list(AGENT_PROMPTS.keys())


def prompt_exists(agent_name: str) -> bool:
    """Check if a prompt file exists for an agent.
    
    Args:
        agent_name: Agent name (full or alias)
        
    Returns:
        True if prompt file exists
    """
    try:
        # Resolve alias
        normalized = agent_name.lower().replace("-", "_")
        if normalized in AGENT_ALIASES:
            full_name = AGENT_ALIASES[normalized]
        elif agent_name in AGENT_PROMPTS:
            full_name = agent_name
        else:
            return False
        
        filename = AGENT_PROMPTS[full_name]
        filepath = PROMPTS_DIR / filename
        return filepath.exists()
        
    except Exception:
        return False


__all__ = [
    "load_prompt",
    "get_all_prompts",
    "get_agent_names",
    "prompt_exists",
    "AGENT_PROMPTS",
    "AGENT_ALIASES",
]

