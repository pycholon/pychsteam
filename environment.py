class Environment:  # as Singleton
    STEAM_API_KEY = "api key "
    MY_STEAM_ID = "steam id"
    DISCORD_TOKEN_1 = "discord token"
    _instance = None

    def __init__(self):
        pass

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance


Env = Environment()
