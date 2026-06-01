import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"


class WeatherService:
    def __init__(self):
        # 🔥 FIX: read env at runtime (NOT module import time)
        self.api_key = os.getenv('OPENWEATHER_API_KEY')

        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY not found")

    def get_weather_forecast(self, destination, start_date, end_date):
        try:
            # -------------------------
            # 1. Geocoding API
            # -------------------------
            geo_url = "http://api.openweathermap.org/geo/1.0/direct"

            geo_params = {
                'q': destination,
                'limit': 1,
                'appid': self.api_key
            }

            geo_response = requests.get(geo_url, params=geo_params)
            geo_response.raise_for_status()

            location_data = geo_response.json()

            if not location_data:
                return {'error': 'Location not found'}, 404

            lat = location_data[0]['lat']
            lon = location_data[0]['lon']

            # -------------------------
            # 2. Forecast API
            # -------------------------
            forecast_url = f"{OPENWEATHER_BASE_URL}/forecast"

            forecast_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }

            forecast_response = requests.get(forecast_url, params=forecast_params)
            forecast_response.raise_for_status()

            data = forecast_response.json()

            # -------------------------
            # 3. Parse dates
            # -------------------------
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            forecast_list = []

            for item in data.get('list', []):
                forecast_date = datetime.fromtimestamp(item['dt']).date()

                if start_date <= forecast_date <= end_date:
                    forecast_list.append({
                        'date': forecast_date.strftime("%Y-%m-%d"),
                        'temperature': round(item['main']['temp']),
                        'condition': item['weather'][0]['description'].capitalize(),
                        'rain_probability': int(item.get('pop', 0) * 100)
                    })

            if not forecast_list:
                return {'error': 'No forecast data available'}, 404

            return {
                'destination': destination,
                'forecast': forecast_list
            }, 200

        except requests.exceptions.RequestException as e:
            return {'error': str(e)}, 500

        except Exception as e:
            return {'error': str(e)}, 500