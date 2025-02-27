from helper.format_api_requests import APIHelper
import requests
from config.config_files import APIkeys
from config.constants import Constants
import yfinance as yf


class APIRequests:
    
    def get_stock_or_crypto_current_price(self, symbol, stock):
        if not stock:
            symbol = f"{symbol}-USD"
        try:
            ticker = yf.Ticker(symbol)
            todays_data = ticker.history(period='1d')
            price = todays_data['Close'].iloc[0]
            return str(round(price, 2))
        except Exception as e:
            print(f"Error fetching data from passed {symbol}: {e}")
            return None

    def get_weather_data(self, location):
        city_id = APIHelper.get_city_id(location)
        if not city_id:
            return f"Invalid location '{location}'. Please try another city."

        url = Constants.WEATHER_URL.format(api_key=APIkeys.weatherAPI, location=city_id)
        weather_json = requests.get(url).json()

        weather_data = APIHelper.extract_weather_info(weather_json)
        if not weather_data:
            return f"Could not retrieve weather data for {location}."

        return (
            f"Current weather in {location}: {weather_data['temp']}°C, "
            f"{weather_data['weather'].lower()} skies, wind speed {weather_data['wind_speed']} m/s."
        )
