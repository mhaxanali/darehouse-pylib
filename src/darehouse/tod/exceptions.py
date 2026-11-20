class GameDoesNotExist(Exception):
    """Error that is raised if method is called but no lobby is created."""
    pass


class GameAlreadyRunning(Exception):
    """Error that is raised if an attempt to start an already running game is made."""
    pass

class GameNotRunning(Exception):
    """Error raised when turn is advanced but no game is running."""
    pass

class GameAlreadyExists(Exception):
    """Error raised if game is tried to be initialized again."""
    pass

class PlayerDoesNotExist(Exception):
    """Error raised if the requested player does not exist in game."""
    pass

class PlayerAlreadyExists(Exception):
    """Error raised if the requested player already exists in game."""
    pass

class InsufficientPlayers(Exception):
    """Error raised if there aren't enough players in the game."""
    pass