import pytest

from darehouse.tod.engine import TODEngine
from darehouse.tod.models import Player, Prompt, PromptType
from darehouse.tod.exceptions import (
    GameAlreadyExists,
    GameAlreadyRunning,
    GameDoesNotExist,
    GameNotRunning,
    InsufficientPlayers,
    PlayerAlreadyExists,
    PlayerDoesNotExist,
)


class MockPromptProvider:
    """Mock implementation of PromptProvider."""

    def __init__(self):
        self.prompts = {
            PromptType.TRUTH: Prompt(
                content="Mock truth prompt",
                type=PromptType.TRUTH,
            ),
            PromptType.DARE: Prompt(
                content="Mock dare prompt",
                type=PromptType.DARE,
            ),
        }

        self.requested_types = []

    def get_prompt(self, prompt_type: PromptType) -> Prompt:
        self.requested_types.append(prompt_type)
        return self.prompts[prompt_type]


@pytest.fixture
def provider():
    return MockPromptProvider()


@pytest.fixture
def engine(provider):
    return TODEngine(
        prompt_provider=provider,
        maximum_prompts_to_keep=3,
    )


@pytest.fixture
def lobby(engine):
    engine.create_lobby()
    return engine


@pytest.fixture
def players():
    return [
        Player(id=1),
        Player(id=2),
        Player(id=3),
    ]


# ============================================================
# Initialization
# ============================================================


def test_engine_initialization(engine):
    assert engine.game is None
    assert engine.maximum_prompts_to_keep == 3


def test_negative_prompt_history_limit():
    with pytest.raises(ValueError):
        TODEngine(
            prompt_provider=MockPromptProvider(),
            maximum_prompts_to_keep=-1,
        )


def test_zero_prompt_history_limit():
    engine = TODEngine(
        prompt_provider=MockPromptProvider(),
        maximum_prompts_to_keep=0,
    )

    assert engine.maximum_prompts_to_keep == 0


# ============================================================
# Lobby management
# ============================================================


def test_create_lobby(engine):
    engine.create_lobby()

    assert engine.game is not None
    assert engine.game.is_running is False
    assert engine.game.players == []
    assert engine.game.current_player_index == 0


def test_create_lobby_twice(lobby):
    with pytest.raises(GameAlreadyExists):
        lobby.create_lobby()


def test_operations_without_lobby(engine):
    with pytest.raises(GameDoesNotExist):
        engine.add_player(Player(id=1))

    with pytest.raises(GameDoesNotExist):
        engine.remove_player(Player(id=1))

    with pytest.raises(GameDoesNotExist):
        engine.start_game()

    with pytest.raises(GameDoesNotExist):
        engine.advance_turn()

    with pytest.raises(GameDoesNotExist):
        engine.get_prompt(PromptType.TRUTH)

    with pytest.raises(GameDoesNotExist):
        engine.end_game()


# ============================================================
# Player management
# ============================================================


def test_add_player(lobby):
    player = Player(id=1)

    lobby.add_player(player)

    assert player in lobby.game.players
    assert len(lobby.game.players) == 1


def test_add_multiple_players(lobby, players):
    for player in players:
        lobby.add_player(player)

    assert lobby.game.players == players


def test_add_duplicate_player(lobby):
    player = Player(id=1)

    lobby.add_player(player)

    with pytest.raises(PlayerAlreadyExists):
        lobby.add_player(player)


def test_remove_player(lobby):
    player1 = Player(id=1)
    player2 = Player(id=2)

    lobby.add_player(player1)
    lobby.add_player(player2)

    lobby.remove_player(player1)

    assert player1 not in lobby.game.players
    assert player2 in lobby.game.players
    assert len(lobby.game.players) == 1


def test_remove_nonexistent_player(lobby):
    lobby.add_player(Player(id=1))
    lobby.add_player(Player(id=2))

    with pytest.raises(PlayerDoesNotExist):
        lobby.remove_player(Player(id=3))


def test_remove_player_from_empty_lobby(lobby):
    with pytest.raises(PlayerDoesNotExist):
        lobby.remove_player(Player(id=1))


def test_remove_last_player(lobby):
    player = Player(id=1)

    lobby.add_player(player)
    lobby.remove_player(player)

    assert lobby.game.players == []
    assert lobby.game.current_player_index == 0


def test_add_player_during_running_game(lobby):
    player1 = Player(id=1)
    player2 = Player(id=2)

    lobby.add_player(player1)
    lobby.start_game()

    lobby.add_player(player2)

    assert player2 in lobby.game.players
    assert len(lobby.game.players) == 2


# ============================================================
# Game lifecycle
# ============================================================


def test_start_game(lobby, players):
    for player in players:
        lobby.add_player(player)

    lobby.start_game()

    assert lobby.game.is_running is True
    assert lobby.game.current_player_index == 0


def test_start_game_without_players(lobby):
    with pytest.raises(InsufficientPlayers):
        lobby.start_game()


def test_start_game_with_one_player(lobby):
    lobby.add_player(Player(id=1))

    lobby.start_game()

    assert lobby.game.is_running is True
    assert lobby.game.current_player_index == 0


def test_start_game_twice(lobby):
    lobby.add_player(Player(id=1))

    lobby.start_game()

    with pytest.raises(GameAlreadyRunning):
        lobby.start_game()


def test_start_game_shuffles_players(lobby, players):
    for player in players:
        lobby.add_player(player)

    original_players = lobby.game.players.copy()

    lobby.start_game()

    assert sorted(
        player.id for player in lobby.game.players
    ) == sorted(
        player.id for player in original_players
    )

    assert lobby.game.is_running is True
    assert lobby.game.current_player_index == 0


def test_start_game_resets_current_player_index(lobby, players):
    for player in players:
        lobby.add_player(player)

    lobby.game.current_player_index = 2

    lobby.start_game()

    assert lobby.game.current_player_index == 0


def test_end_game(lobby):
    lobby.add_player(Player(id=1))

    lobby.start_game()
    lobby.end_game()

    assert lobby.game is None


def test_end_game_without_running_game(lobby):
    lobby.end_game()

    assert lobby.game is None


# ============================================================
# Turn management
# ============================================================


def test_advance_turn(lobby, players):
    for player in players:
        lobby.add_player(player)

    lobby.start_game()

    lobby.game.current_player_index = 0

    lobby.advance_turn()

    assert lobby.game.current_player_index == 1


def test_advance_turn_wraps_around(lobby, players):
    for player in players:
        lobby.add_player(player)

    lobby.start_game()

    lobby.game.current_player_index = (
        len(lobby.game.players) - 1
    )

    lobby.advance_turn()

    assert lobby.game.current_player_index == 0


def test_advance_turn_with_one_player(lobby):
    lobby.add_player(Player(id=1))

    lobby.start_game()
    lobby.advance_turn()

    assert lobby.game.current_player_index == 0


def test_advance_turn_without_running_game(lobby):
    lobby.add_player(Player(id=1))

    with pytest.raises(GameNotRunning):
        lobby.advance_turn()


def test_advance_turn_with_zero_players(lobby):
    lobby.game.is_running = True

    with pytest.raises(InsufficientPlayers):
        lobby.advance_turn()


# ============================================================
# Player removal during a running game
# ============================================================


def test_remove_player_before_current_player(lobby, players):
    for player in players:
        lobby.add_player(player)

    lobby.start_game()

    lobby.game.players = players.copy()
    lobby.game.current_player_index = 2

    lobby.remove_player(players[0])

    assert lobby.game.players == [
        players[1],
        players[2],
    ]

    assert lobby.game.current_player_index == 1


def test_remove_current_player(lobby, players):
    for player in players:
        lobby.add_player(player)

    lobby.start_game()

    lobby.game.players = players.copy()
    lobby.game.current_player_index = 1

    lobby.remove_player(players[1])

    assert lobby.game.players == [
        players[0],
        players[2],
    ]

    assert lobby.game.current_player_index == 0

    lobby.advance_turn()

    assert lobby.game.current_player_index == 1
    assert lobby.game.players[
        lobby.game.current_player_index
    ] == players[2]


def test_remove_player_after_current_player(lobby, players):
    for player in players:
        lobby.add_player(player)

    lobby.start_game()

    lobby.game.players = players.copy()
    lobby.game.current_player_index = 0

    lobby.remove_player(players[2])

    assert lobby.game.players == [
        players[0],
        players[1],
    ]

    assert lobby.game.current_player_index == 0


def test_remove_first_player_wraps_current_index(lobby, players):
    for player in players:
        lobby.add_player(player)

    lobby.start_game()

    lobby.game.players = players.copy()
    lobby.game.current_player_index = 0

    lobby.remove_player(players[0])

    assert lobby.game.players == [
        players[1],
        players[2],
    ]

    assert lobby.game.current_player_index == 1

    lobby.advance_turn()

    assert lobby.game.current_player_index == 0


def test_remove_last_player_during_running_game(lobby):
    player = Player(id=1)

    lobby.add_player(player)
    lobby.start_game()

    lobby.remove_player(player)

    assert lobby.game.players == []
    assert lobby.game.current_player_index == 0


def test_remove_player_from_running_game_with_one_player(lobby):
    player = Player(id=1)

    lobby.add_player(player)
    lobby.start_game()

    lobby.remove_player(player)

    assert lobby.game.players == []
    assert lobby.game.current_player_index == 0

    with pytest.raises(InsufficientPlayers):
        lobby.advance_turn()


# ============================================================
# Prompt management
# ============================================================


def test_get_truth_prompt(engine, provider):
    engine.create_lobby()

    prompt = engine.get_prompt(PromptType.TRUTH)

    assert prompt.content == "Mock truth prompt"
    assert prompt.type == PromptType.TRUTH

    assert provider.requested_types == [
        PromptType.TRUTH
    ]


def test_get_dare_prompt(engine, provider):
    engine.create_lobby()

    prompt = engine.get_prompt(PromptType.DARE)

    assert prompt.content == "Mock dare prompt"
    assert prompt.type == PromptType.DARE

    assert provider.requested_types == [
        PromptType.DARE
    ]


def test_prompt_history(engine):
    engine.create_lobby()

    engine.get_prompt(PromptType.TRUTH)
    engine.get_prompt(PromptType.DARE)

    assert len(engine.game.last_prompts) == 2


def test_prompt_history_limit(engine):
    engine.create_lobby()

    engine.get_prompt(PromptType.TRUTH)
    engine.get_prompt(PromptType.DARE)
    engine.get_prompt(PromptType.TRUTH)
    engine.get_prompt(PromptType.DARE)

    assert len(engine.game.last_prompts) == 3


def test_prompt_history_keeps_latest_prompts(engine):
    engine.create_lobby()

    first = engine.get_prompt(PromptType.TRUTH)
    second = engine.get_prompt(PromptType.DARE)
    third = engine.get_prompt(PromptType.TRUTH)
    fourth = engine.get_prompt(PromptType.DARE)

    assert engine.game.last_prompts == [
        second,
        third,
        fourth,
    ]


def test_zero_prompt_history(engine):
    engine.maximum_prompts_to_keep = 0

    engine.create_lobby()

    prompt = engine.get_prompt(PromptType.TRUTH)

    assert prompt is not None
    assert engine.game.last_prompts == []