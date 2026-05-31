import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"


class WeatherService:
    def __init__(self):
        if not OPENWEATHER_API_KEY:
            raise ValueError("OPENWEATHER_API_KEY not found in environment variables")
    
    def get_weather_forecast(self, destination, start_date, end_date):
        """
        Fetch weather forecast for a destination between start_date and end_date.
        
        Args:
            destination: City name (e.g., "Auckland")
            start_date: Journey start date (datetime or date object)
            end_date: Journey end date (datetime or date object)
            
        Returns:
            dict with destination and forecast list
        """
        try:
            # Get coordinates for the city
            geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct"
            params = {
                'q': destination,
                'limit': 1,
                'appid': OPENWEATHER_API_KEY
            }
            
            response = requests.get(geocoding_url, params=params)
            response.raise_for_status()
            
            location_data = response.json()
            if not location_data:
                return {'error': f'Location not found: {destination}'}, 404
            
            lat = location_data[0]['lat']
            lon = location_data[0]['lon']
            
            # Get 5-day forecast
            forecast_url = f"{OPENWEATHER_BASE_URL}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            
            response = requests.get(forecast_url, params=params)
            response.raise_for_status()
            
            forecast_data = response.json()
            
            # Filter forecast for journey dates
            forecast_list = []
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            for item in forecast_data['list']:
                forecast_date = datetime.fromtimestamp(item['dt']).date()
                if start_date <= forecast_date <= end_date:
                    forecast_list.append({
                        'date': forecast_date.strftime('%Y-%m-%d'),
                        'temperature': round(item['main']['temp']),
                        'condition': item['weather'][0]['description'].capitalize(),
                        'rain_probability': int(item.get('pop', 0) * 100)
                    })
            
            if not forecast_list:
                return {'error': 'No forecast data available for the specified dates'}, 404
            
            return {
                'destination': destination,
                'forecast': forecast_list
            }, 200
            
        except requests.exceptions.RequestException as e:
            return {'error': f'Failed to fetch weather data: {str(e)}'}, 500
        except Exception as e:
            return {'error': f'An error occurred: {str(e)}'}, 500
