# Usage

This document covers the usage of `darehouse`, including initialization, prompt providers, lobby management, player management, game lifecycle, turn management, and prompt history.

## Installation

Install the library from PyPI:

```bash
pip install darehouse
```

Alternatively, install directly from source:

```bash
git clone https://github.com/mhaxanali/darehouse-pylib.git
cd darehouse-pylib
pip install -e .
```

## Truth or Dare Engine

The Truth or Dare engine is available through `darehouse.tod`.

```python
from darehouse.tod.engine import TODEngine
from darehouse.tod.models import Player, Prompt, PromptType
```

The engine manages the game state while delegating prompt generation to a user-defined prompt provider.

## 1. Creating a Prompt Provider

The engine requires an object implementing the `PromptProvider` protocol.

A prompt provider is responsible for generating and returning prompts based on the requested prompt type.

```python
from darehouse.tod.models import Prompt, PromptType


class MyPromptProvider:

    def get_prompt(self, prompt_type: PromptType) -> Prompt:
        prompts = {
            PromptType.TRUTH: [
                "What is something you are proud of?",
                "What is your favourite memory?",
                "What is a skill you would like to learn?",
            ],
            PromptType.DARE: [
                "Speak in a different accent for the next minute.",
                "Draw something with your eyes closed.",
                "Try to name five countries in ten seconds.",
            ],
        }

        import random

        content = random.choice(prompts[prompt_type])

        return Prompt(
            content=content,
            type=prompt_type,
        )
```

The prompt provider can use any source of prompts, including:

- Static collections
- Databases
- External APIs
- Randomized prompt selection
- Application-specific logic

The engine does not manage the storage or selection of prompts.

## 2. Initializing the Engine

Create an instance of `TODEngine` by providing a prompt provider and a prompt history limit.

```python
from darehouse.tod.engine import TODEngine

engine = TODEngine(
    prompt_provider=MyPromptProvider(),
    maximum_prompts_to_keep=10,
)
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `prompt_provider` | `PromptProvider` | The object responsible for generating prompts |
| `maximum_prompts_to_keep` | `int` | Maximum number of prompts retained in history |

A negative history limit raises `ValueError`.

Setting the history limit to `0` disables prompt history retention.

## 3. Creating a Lobby

Before adding players or performing game operations, create a lobby.

```python
engine.create_lobby()
```

Each engine instance manages one lobby at a time.

Attempting to create another lobby while one already exists raises `GameAlreadyExists`.

## 4. Managing Players

Players are represented by the `Player` model.

```python
from darehouse.tod.models import Player

player1 = Player(id=1)
player2 = Player(id=2)
player3 = Player(id=3)
```

### Adding Players

```python
engine.add_player(player1)
engine.add_player(player2)
engine.add_player(player3)
```

Players can also be added individually as needed.

Attempting to add a player who already exists in the lobby raises `PlayerAlreadyExists`.

### Removing Players

```python
engine.remove_player(player2)
```

Attempting to remove a player who is not in the lobby raises `PlayerDoesNotExist`.

Player management is not restricted to the pre-game phase. Players may be added or removed while the game is running.

## 5. Starting the Game

Once the lobby has been created and players have been added, start the game.

```python
engine.start_game()
```

The engine shuffles the player order when the game starts.

Starting a game with an empty lobby raises `InsufficientPlayers`.

Attempting to start an already running game raises `GameAlreadyRunning`.

## 6. Accessing Game State

The current game state is accessible through the engine's `game` attribute.

```python
game = engine.game
```

The `GameState` model contains the following attributes:

| Attribute | Type | Description |
|---|---|---|
| `players` | `list[Player]` | Players currently in the lobby/game |
| `last_prompts` | `list[Prompt]` | Previously generated prompts retained in history |
| `current_player_index` | `int` | Index of the current player |
| `is_running` | `bool` | Whether the game is currently running |

### Getting the Current Player

```python
current_player = engine.game.players[
    engine.game.current_player_index
]

print(current_player.id)
```

The current player is determined by `current_player_index`.

## 7. Advancing Turns

Advance to the next player using:

```python
engine.advance_turn()
```

The engine increments the current player index and wraps around to the beginning of the player list when the end is reached.

For example:

```text
Player 1 -> Player 2 -> Player 3 -> Player 1
```

Attempting to advance a turn while the game is not running raises `GameNotRunning`.

Attempting to advance a turn while there is no player in the lobby raises `InsufficientPlayers`.

## 8. Getting Prompts

Prompts can be requested using the `PromptType` enumeration.

### Truth

```python
truth = engine.get_prompt(PromptType.TRUTH)

print(truth.content)
```

### Dare

```python
dare = engine.get_prompt(PromptType.DARE)

print(dare.content)
```

The returned `Prompt` object contains:

| Attribute | Type | Description |
|---|---|---|
| `content` | `str` | The prompt text |
| `type` | `PromptType` | The prompt category |

Every generated prompt is passed through the configured prompt provider.

Prompts are recorded in the game's history, subject to the configured history limit.

## 9. Prompt History

The engine maintains a history of recently generated prompts.

```python
history = engine.game.last_prompts
```

The history is limited by `maximum_prompts_to_keep`.

When the limit is exceeded, the oldest prompt is removed.

For example, with a history limit of `3`:

```text
Prompt 1 -> [Prompt 1]
Prompt 2 -> [Prompt 1, Prompt 2]
Prompt 3 -> [Prompt 1, Prompt 2, Prompt 3]
Prompt 4 -> [Prompt 2, Prompt 3, Prompt 4]
```

To disable history:

```python
engine = TODEngine(
    prompt_provider=MyPromptProvider(),
    maximum_prompts_to_keep=0,
)
```

The engine will still return generated prompts, but they will not be retained.

## 10. Ending the Game

End the current game using:

```python
engine.end_game()
```

This removes the current game state from the engine.

After ending the game, a new lobby can be created:

```python
engine.end_game()

engine.create_lobby()
engine.add_player(Player(id=4))
```

## Complete Example

```python
from darehouse.tod.engine import TODEngine
from darehouse.tod.models import Player, Prompt, PromptType


class MyPromptProvider:

    def get_prompt(self, prompt_type: PromptType) -> Prompt:
        prompts = {
            PromptType.TRUTH: "What is something you would like to accomplish?",
            PromptType.DARE: "Do your best impression of a fictional character.",
        }

        return Prompt(
            content=prompts[prompt_type],
            type=prompt_type,
        )


engine = TODEngine(
    prompt_provider=MyPromptProvider(),
    maximum_prompts_to_keep=5,
)

# Create a lobby
engine.create_lobby()

# Add players
engine.add_player(Player(id=1))
engine.add_player(Player(id=2))
engine.add_player(Player(id=3))

# Start the game
engine.start_game()

# Get the current player
current_player = engine.game.players[
    engine.game.current_player_index
]

print(f"Current player: {current_player.id}")

# Generate a prompt
prompt = engine.get_prompt(PromptType.TRUTH)

print(f"{prompt.type.value}: {prompt.content}")

# Advance to the next player
engine.advance_turn()

# Get the new current player
current_player = engine.game.players[
    engine.game.current_player_index
]

print(f"Next player: {current_player.id}")

# Generate another prompt
prompt = engine.get_prompt(PromptType.DARE)

print(f"{prompt.type.value}: {prompt.content}")

# End the game
engine.end_game()
```

## Error Handling

The engine raises custom exceptions when invalid operations are performed.

For a complete list of exceptions and their causes, refer to [`EXCEPTIONS.md`](EXCEPTIONS.md).

Applications should handle exceptions where appropriate rather than relying on exception messages.

## Notes

- Each `TODEngine` instance manages its own game state.
- The engine does not manage Discord users, messages, channels, or interactions.
- Player identifiers are managed by the integrating application.
- Prompt generation is delegated to the configured prompt provider.
- Player order is shuffled when a game starts.
- Players may be added or removed during a running game.
- The engine does not implement a user interface.
- The game state is accessible through the engine's `game` attribute.
