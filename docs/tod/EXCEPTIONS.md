# Exceptions

This document describes the exceptions raised by `darehouse` and the circumstances under which they occur.

All custom exceptions are defined in `darehouse.tod.exceptions`.

## Exception Hierarchy

```text
Exception
├── GameDoesNotExist
├── GameAlreadyExists
├── GameAlreadyRunning
├── GameNotRunning
├── PlayerAlreadyExists
├── PlayerDoesNotExist
└── InsufficientPlayers
```

All exceptions currently inherit directly from Python's built-in `Exception` class.

## Exceptions

### `GameDoesNotExist`

Raised when an operation requires an existing game or lobby, but none has been created.

**Common causes:**
- Attempting to add a player before creating a lobby.
- Attempting to remove a player when no lobby exists.
- Attempting to start a game without an existing lobby.
- Attempting to retrieve a prompt without an existing game.

---

### `GameAlreadyExists`

Raised when attempting to create a lobby while one already exists.

**Common causes:**
- Calling `create_lobby()` multiple times without ending the existing game.

---

### `GameAlreadyRunning`

Raised when attempting to start a game that is already running.

**Common causes:**
- Calling `start_game()` more than once during the same game session.

---

### `GameNotRunning`

Raised when attempting to perform an operation that requires an active game, but the game is not running.

**Common causes:**
- Attempting to advance the turn before starting the game.
- Attempting to advance the turn after the game has ended.

---

### `PlayerAlreadyExists`

Raised when attempting to add a player who is already present in the lobby.

**Common causes:**
- Adding the same player more than once.

---

### `PlayerDoesNotExist`

Raised when attempting to remove a player who is not present in the lobby.

**Common causes:**
- Attempting to remove a player who was never added.
- Attempting to remove a player who has already been removed.

---

### `InsufficientPlayers`

Raised when an operation requires a minimum number of players, but the current lobby does not meet that requirement.

**Common causes:**
- Attempting to start a game with an empty lobby.
- Attempting to remove a player when fewer than two players remain.

## Handling Exceptions

Applications using `darehouse` should handle exceptions where appropriate to prevent unexpected failures and provide meaningful feedback to their users.

```python
from darehouse.tod.engine import TODEngine
from darehouse.tod.exceptions import (
    GameAlreadyExists,
    InsufficientPlayers,
)

engine = TODEngine(
    prompt_provider=my_prompt_provider,
    maximum_prompts_to_keep=10,
)

try:
    engine.create_lobby()
    engine.start_game()

except GameAlreadyExists:
    print("A lobby already exists.")

except InsufficientPlayers:
    print("Not enough players to start the game.")
```

Exceptions should generally be handled by the application integrating the library rather than suppressed within the library itself.

## Notes

- Exceptions are raised synchronously by the engine.
- Exceptions do not automatically terminate the application.
- Exception messages are intended to provide additional context but should not be relied upon for programmatic error handling.
- Applications should catch exception types rather than compare exception messages.
- This list may expand as additional game engines and functionality are introduced.
