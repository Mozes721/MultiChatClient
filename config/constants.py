from dataclasses import dataclass


@dataclass
class Constants:
    WEATHER_URL: str = (
        "http://api.openweathermap.org/data/2.5/weather?appid={api_key}"
        "&id={location}"
    )