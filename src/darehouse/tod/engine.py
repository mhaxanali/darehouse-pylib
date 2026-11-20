from .models import *
from .protocols import *
from .exceptions import *

import random

class TODEngine:
    """Game Engine for Truth or Dare."""

    def __init__(self, prompt_provider: PromptProvider, maximum_prompts_to_keep: int):
        self.prompt_provider = prompt_provider
        if maximum_prompts_to_keep < 0:
            raise ValueError(
                "maximum_prompts_to_keep cannot be negative."
            )
        self.maximum_prompts_to_keep = maximum_prompts_to_keep
        self.game: GameState | None = None

    def get_prompt(self, prompt_type: PromptType) -> Prompt:
        self.check_game()

        prompt = self.prompt_provider.get_prompt(prompt_type)

        self.game.last_prompts.append(prompt)

        if len(self.game.last_prompts) > self.maximum_prompts_to_keep:
            self.game.last_prompts.pop(0)

        return prompt
    
    def check_game(self):
        if self.game is None:
            raise GameDoesNotExist("The game you're trying to modify doesn't exist.")

    def create_lobby(self):
        if self.game:
            raise GameAlreadyExists("A lobby already exists.")
        self.game = GameState()

    def add_player(self, player: Player):
        self.check_game()
        if player in self.game.players:
            raise PlayerAlreadyExists("The player is already in game.")
        self.game.players.append(player)

    def remove_player(self, player: Player):
        self.check_game()
        if player not in self.game.players:
            raise PlayerDoesNotExist("The player is not in the game.")
        if len(self.game.players) < 2:
            raise InsufficientPlayers("There must be at least two players in order to remove one.")
        self.game.players.remove(player)

    def start_game(self):
        self.check_game()
        if len(self.game.players) < 1:
            raise InsufficientPlayers("Cannot start a game with zero players.")
        if self.game.is_running:
            raise GameAlreadyRunning("The current lobby is already playing a game.")
        random.shuffle(self.game.players)
        self.game.is_running = True

    def advance_turn(self):
        self.check_game()
        if not self.game.is_running:
            raise GameNotRunning("The game you're trying to advance doesn't exist.")
        if self.game.current_player_index == len(self.game.players)-1:
            self.game.current_player_index = 0
        else:
            self.game.current_player_index+=1

    def end_game(self):
        self.check_game()
        self.game = None
        