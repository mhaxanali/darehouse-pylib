from typing import Protocol
from .models import Prompt, PromptType


class PromptProvider(Protocol):
    def get_prompt(self, prompt_type: PromptType) -> Prompt:
        ...