import os
from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass
from distutils.util import strtobool

load_dotenv(find_dotenv())


@dataclass(frozen=True)
class APIkeys:
    deployment: bool = bool(strtobool(os.getenv('DEPLOYMENT')))
    weatherAPI: str = os.getenv('WEATHER_API_KEY')
    discordClientID: str = os.getenv('DISCORD_CLIENT_ID')
    discordToken: str = os.getenv('DISCORD_TOKEN')
