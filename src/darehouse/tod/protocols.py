from typing import Protocol
from .models import Prompt, PromptType


class PromptProvider(Protocol):
    """Protocol for objects that provide Truth or Dare prompts.

    Implementations of this protocol are responsible for generating
    prompts of the requested type. The prompt-generation logic is
    intentionally left to the consumer of the library.

    This allows the game engine to work with different prompt
    sources, such as predefined prompt lists, databases, APIs,
    or custom implementations.
    """

    def get_prompt(self, prompt_type: PromptType) -> Prompt:
        """Retrieve a prompt of the specified type.

        Args:
            prompt_type: The type of prompt to retrieve, either
                truth or dare.

        Returns:
            A Prompt instance matching the requested type.
        """
        ...