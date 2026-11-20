from dataclasses import dataclass, field
from enum import Enum


class PromptType(Enum):
    """Types of prompts available in Truth or Dare."""

    TRUTH = "truth"
    """A truth prompt, asking a player to answer a question."""

    DARE = "dare"
    """A dare prompt, asking a player to complete a challenge."""


@dataclass
class Player:
    """Represents a player participating in a game.

    Attributes:
        id: Unique identifier for the player.
    """

    id: int


@dataclass
class Prompt:
    """Represents a Truth or Dare prompt.

    Attributes:
        content: The text of the prompt.
        type: The category of the prompt, either truth or dare.
    """

    content: str
    type: PromptType


@dataclass
class GameState:
    """Represents the current state of a Truth or Dare game.

    Attributes:
        players: List of players participating in the game.
        last_prompts: History of recently generated prompts.
        current_player_index: Index of the player whose turn it is.
        is_running: Whether the game is currently in progress.
    """

    players: list[Player] = field(default_factory=list)
    last_prompts: list[Prompt] = field(default_factory=list)
    current_player_index: int = 0
    is_running: bool = False