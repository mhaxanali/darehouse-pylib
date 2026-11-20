from dataclasses import dataclass
from enum import Enum

class PromptType(Enum):
    TRUTH = "truth"
    DARE = "dare"

@dataclass
class Player:
    id: int

@dataclass
class Prompt:
    content: str
    type: PromptType

@dataclass
class GameState:
    players: list[Player] = []
    last_prompts: list[Prompt] = []
    current_player_index: int = 0
    is_running: bool = False