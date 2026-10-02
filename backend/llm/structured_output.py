from typing import Dict, Any, Type, Optional
from pydantic import BaseModel
from .provider import get_llm_provider

def generate_structured_response(
    prompt: str,
    system_prompt: str,
    schema_class: Type[BaseModel]
) -> Dict[str, Any]:
    """
    Generate and validate a structured JSON object matching a Pydantic schema class.
    """
    provider = get_llm_provider()
    json_prompt = f"{prompt}\n\nSchema Requirements (JSON):\n{schema_class.schema_json()}"
    return provider.generate_structured(prompt=json_prompt, system_prompt=system_prompt, schema_class=schema_class)
