from .models import *
from .protocols import *
from .exceptions import *

import random


class TODEngine:
    """Engine for managing Truth or Dare game sessions.

    Handles lobby management, player management, game lifecycle,
    turn progression, and prompt history.

    Prompt generation is delegated to the configured prompt provider.
    Each engine instance manages a single game session at a time.
    """

    def __init__(
        self,
        prompt_provider: PromptProvider,
        maximum_prompts_to_keep: int,
    ):
        """Initialize the Truth or Dare engine.

        Args:
            prompt_provider: Provider responsible for generating
                truth and dare prompts.
            maximum_prompts_to_keep: Maximum number of prompts
                retained in game history. Zero disables history
                retention.

        Raises:
            ValueError: If maximum_prompts_to_keep is negative.
        """
        self.prompt_provider = prompt_provider

        if maximum_prompts_to_keep < 0:
            raise ValueError(
                "maximum_prompts_to_keep cannot be negative."
            )

        self.maximum_prompts_to_keep = maximum_prompts_to_keep
        self.game: GameState | None = None

    def get_prompt(self, prompt_type: PromptType) -> Prompt:
        """Generate and return a prompt of the specified type.

        Requests a prompt from the configured prompt provider
        and adds it to the game's prompt history, subject to
        the configured history limit.

        Args:
            prompt_type: The category of prompt to generate.

        Returns:
            The generated prompt.

        Raises:
            GameDoesNotExist: If no lobby exists.
        """
        self.check_game()

        prompt = self.prompt_provider.get_prompt(prompt_type)

        self.game.last_prompts.append(prompt)

        if len(self.game.last_prompts) > self.maximum_prompts_to_keep:
            self.game.last_prompts.pop(0)

        return prompt

    def check_game(self):
        """Ensure that a game state currently exists.

        Raises:
            GameDoesNotExist: If no lobby or game state exists.
        """
        if self.game is None:
            raise GameDoesNotExist(
                "The game you're trying to modify doesn't exist."
            )

    def create_lobby(self):
        """Create a new lobby with an empty game state.

        The newly created lobby contains no players and is not
        running.

        Raises:
            GameAlreadyExists: If a lobby already exists.
        """
        if self.game is not None:
            raise GameAlreadyExists("A lobby already exists.")

        self.game = GameState()

    def add_player(self, player: Player):
        """Add a player to the current lobby.

        Players may be added before or during a running game.
        A player added during a running game joins at the end of
        the player order.

        Args:
            player: The player to add.

        Raises:
            GameDoesNotExist: If no lobby exists.
            PlayerAlreadyExists: If the player is already present.
        """
        self.check_game()

        if player in self.game.players:
            raise PlayerAlreadyExists(
                "The player is already in game."
            )

        self.game.players.append(player)

    def remove_player(self, player: Player):
        """Remove a player from the current lobby.

        Players may be removed before or during a running game.

        While the game is running, the current player index is
        adjusted so that the next call to advance_turn moves to
        the player who would have followed in the original order,
        regardless of who was removed:

        - Removing a player before the current player shifts the
          list, so the index is moved back to keep pointing at
          the same player.
        - Removing the current player moves the index back one
          position, so the next advance_turn lands on their
          successor (wrapping to the end of the list if needed).
        - If no players remain, the index is reset to zero.

        Args:
            player: The player to remove.

        Raises:
            GameDoesNotExist: If no lobby exists.
            PlayerDoesNotExist: If the player is not present.
        """
        self.check_game()

        if player not in self.game.players:
            raise PlayerDoesNotExist(
                "The player is not in the game."
            )

        removed_index = self.game.players.index(player)
        self.game.players.remove(player)

        if not self.game.is_running:
            return

        if not self.game.players:
            self.game.current_player_index = 0
            return

        if removed_index <= self.game.current_player_index:
            self.game.current_player_index -= 1

            if self.game.current_player_index < 0:
                self.game.current_player_index = (
                    len(self.game.players) - 1
                )

    def start_game(self):
        """Start the current game.

        Shuffles the player order and marks the game as running.

        Raises:
            GameDoesNotExist: If no lobby exists.
            InsufficientPlayers: If the lobby contains no players.
            GameAlreadyRunning: If the game is already running.
        """
        self.check_game()

        if len(self.game.players) < 1:
            raise InsufficientPlayers(
                "Cannot start a game with zero players."
            )

        if self.game.is_running:
            raise GameAlreadyRunning(
                "The current lobby is already playing a game."
            )

        random.shuffle(self.game.players)
        self.game.current_player_index = 0
        self.game.is_running = True

    def advance_turn(self):
        """Advance the current player index.

        Moves to the next player in the current player order.
        Wraps around to the beginning when the final player
        is reached.

        Raises:
            GameDoesNotExist: If no lobby exists.
            GameNotRunning: If the game is not running.
            InsufficientPlayers: If there are no players to
                advance between.
        """
        self.check_game()

        if not self.game.is_running:
            raise GameNotRunning(
                "The game you're trying to advance doesn't exist."
            )

        if not self.game.players:
            raise InsufficientPlayers(
                "Cannot advance the turn with zero players."
            )

        self.game.current_player_index = (
            self.game.current_player_index + 1
        ) % len(self.game.players)

    def end_game(self):
        """End the current game and discard its game state.

        Removes the current lobby and game state from the engine.
        A new lobby may subsequently be created using create_lobby().

        Raises:
            GameDoesNotExist: If no lobby exists.
        """
        self.check_game()
        self.game = None