import json
import os
import re
import requests
from config.config_files import APIkeys
from config.constants import Constants  # Import the Constants class

class APIHelper:
    def __init__(self):
        self.constants = Constants()

    @staticmethod
    def extract_crypto_info(crypto_data):
        crypto_name = crypto_data['data']['1']['name']
        crypto_symbol = crypto_data['data']['1']['symbol']
        crypto_price = crypto_data['data']['1']['quote']['USD']['price']
        crypto_market_cap = crypto_data['data']['1']['quote']['USD']['market_cap']

        formatted_price = "{:.2f}".format(crypto_price)
        formatted_market_cap = "{:.2f}".format(crypto_market_cap)

        return (
            crypto_name,
            crypto_symbol,
            formatted_price,
            formatted_market_cap
            
        )
    @staticmethod
    def extract_stock_info(stock_data, ticker):
        if not stock_data or "values" not in stock_data:
            return f"No stock data found for {ticker}."

        values = stock_data.get("values", [])

        if not values or not isinstance(values, list):
            return f"Unexpected stock data format for {ticker}."

        latest_data = values[0] 
        open_price = latest_data.get("open")

        try:
            open_price = float(open_price)
        except (TypeError, ValueError):
            return f"Open price data unavailable for {ticker}."

        return f"Current price of {ticker} is {open_price:.2f}"


    @staticmethod
    def get_city_id(city):
        json_file_path = os.path.join(os.path.dirname(__file__), 'city_list.json')
        with open(json_file_path) as json_file:
            data = json.load(json_file)
            for item in data:
                if item['name'] == city:
                    return item['id']
        return None

    @staticmethod
    def extract_weather_info(weather_data):
        weather_info = {}

        weather_info['weather'] = weather_data['weather'][0]['main']
        temp = str(weather_data['main']['temp'])
        weather_info['temp'] = temp[:2] + '.' + temp[2:3]
        weather_info['wind_speed'] = weather_data['wind']['speed']

        return weather_info

    def _normalize_company_name(self, name: str) -> str:
        """Normalize company names by removing common suffixes and special characters."""
        # Remove special characters and convert to lowercase
        name = re.sub(r'[^\w\s]', '', name).lower().strip()
        
        # Common company suffixes to remove
        suffixes = [
            'inc', 'incorporated', 'corp', 'corporation', 'ltd', 'limited',
            'llc', 'plc', 'holdings', 'group', 'company', 'co', 'technologies',
            'technology', 'solutions'
        ]
        
        # Remove suffixes if they appear as whole words
        name_parts = name.split()
        filtered_parts = [part for part in name_parts 
                         if part not in suffixes]
        
        return ' '.join(filtered_parts)

    def lookup_ticker_by_name(self, name: str, category: str) -> str:
        """
        Enhanced ticker lookup with better name processing and caching.
        Returns the symbol if found, otherwise returns "Symbol not found".
        """
        # If input is already a valid ticker symbol, return it
        if name.isupper() and 1 <= len(name) <= 5:
            return name
        
        normalized_name = name
        if category == "stock":
            normalized_name = self._normalize_company_name(name)
        
        if category == "crypto":
            return self._lookup_crypto_symbol(normalized_name)
        elif category == "stock":
            return self._lookup_stock_symbol(normalized_name)
        
        return "Symbol not found"

    def _lookup_crypto_symbol(self, name: str) -> str:
        """Look up cryptocurrency symbol using CoinMarketCap API."""
        try:
            self.constants.CRYPTO_PARAMETERS["slug"] = name
            self.constants.CRYPTO_HEADERS["X-CMC_PRO_API_KEY"] = APIkeys.cryptoAPI

            response = requests.get(
                self.constants.CRYPTO_URL,
                headers=self.constants.CRYPTO_HEADERS,
                params=self.constants.CRYPTO_PARAMETERS
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    print(next(iter(data["data"].values()))["symbol"].upper())
                    return next(iter(data["data"].values()))["symbol"].upper()
            
            return "Symbol not found"
        except Exception as e:
            print(f"Error in crypto lookup: {str(e)}")
            return "Symbol not found"

    def _lookup_stock_symbol(self, name: str) -> str:
        """Look up stock symbol using Twelve Data API with fuzzy matching."""
        try:
            url = self.constants.STOCK_URL.format(
                symbol=name.replace(' ', '%20'),
                api_key=APIkeys.stockAPI
            )
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    matches = data["data"]
                    # Sort matches by relevance (you might want to customize this)
                    matches.sort(key=lambda x: len(x.get("name", "")))
                    return matches[0]["symbol"].upper()
            
            return "Symbol not found"
        except Exception as e:
            print(f"Error in stock lookup: {str(e)}")
            return "Symbol not found"