

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class GameCrashError(Error):
    def __init__(self, room=None):
        if room:
            players = [getattr(bot, "token", "Unknown") for bot in room.bots]
            msg = "Seed: {} Players: {}".format(room.seed, players)
        else:
            msg = "No room :("
        super().__init__(msg)
        self.seed = room.seed
        self.bots = room.bots
