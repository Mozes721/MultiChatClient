from typing import Optional
import requests
from config.config_files import APIkeys
from config.constants import Constants


class APIClient:
    """API client for fetching stock, crypto, and weather data."""
    
    @staticmethod   
    def get_financial_data(symbol: str, is_crypto: bool = False) -> Optional[str]:
        try:
            # Twelve Data expects:
            #   - Stocks: "AAPL"
            #   - Crypto: "BTC/USD"
            if is_crypto:
                base = symbol.split("-")[0] if "-" in symbol else symbol
                td_symbol = f"{base}/USD"
            else:
                td_symbol = symbol

            params = {"symbol": td_symbol, "apikey": APIkeys.twelve_data_api_key}
            resp = requests.get("https://api.twelvedata.com/price", params=params, timeout=10)
            data = resp.json()

            price_str = data.get("price")
            if price_str is None:
                msg = data.get("message", f"HTTP {resp.status_code}")
                print(f"Error fetching financial data from Twelve Data for {td_symbol}: {msg}")
                return None

            price = float(price_str)
            return f"price={round(price, 2)}"

        except Exception as e:
            print(f"Error fetching financial data from Twelve Data for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_weather_data(location: str) -> Optional[str]:
        try:
            url = Constants.WEATHER_URL.format(api_key=APIkeys.weatherAPI, location=location)
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                temp = round(data['main']['temp'], 1)
                weather = data['weather'][0]['main'].lower()
                wind = data['wind']['speed']
                return f"temp={temp} weather={weather} wind_speed={wind}"
            elif response.status_code == 404:
                print(f"City not found: {location}")
                return None
            else:
                print(f"Weather API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None

