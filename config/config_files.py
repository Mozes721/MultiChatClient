import os
from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass
from distutils.util import strtobool # type: ignore

load_dotenv(find_dotenv())


@dataclass(frozen=True)
class APIkeys:
    deployment: bool = bool(strtobool(os.getenv('DEPLOYMENT')))
    weatherAPI: str = os.getenv('WEATHER_API_KEY')
    hf_token: str = os.getenv('HUGGING_FACE_TOKEN')
    pinecone_api_key: str = os.getenv('PINECONE_API_KEY')
    twelve_data_api_key: str = os.getenv('TWELVE_DATA_API_KEY')
    discordClientID: str = os.getenv('DISCORD_CLIENT_ID')
    discordToken: str = os.getenv('DISCORD_TOKEN')
