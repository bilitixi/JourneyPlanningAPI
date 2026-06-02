import os
import requests
from collections import Counter
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"


class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")

        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY not found")

    def get_weather_forecast(self, destination, start_date, end_date):
        try:
            # -------------------------
            # Parse dates
            # -------------------------
            if isinstance(start_date, str):
                start_date = datetime.strptime(
                    start_date,
                    "%Y-%m-%d"
                ).date()

            if isinstance(end_date, str):
                end_date = datetime.strptime(
                    end_date,
                    "%Y-%m-%d"
                ).date()

            if start_date > end_date:
                return {
                    "error": "start_date must be before end_date"
                }, 400

            # -------------------------
            # Get coordinates
            # -------------------------
            geo_response = requests.get(
                GEOCODING_URL,
                params={
                    "q": destination,
                    "limit": 1,
                    "appid": self.api_key
                },
                timeout=10
            )

            geo_response.raise_for_status()

            locations = geo_response.json()

            if not locations:
                return {
                    "error": f"Location '{destination}' not found"
                }, 404

            lat = locations[0]["lat"]
            lon = locations[0]["lon"]

            # -------------------------
            # Get forecast
            # -------------------------
            forecast_response = requests.get(
                f"{OPENWEATHER_BASE_URL}/forecast",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric"
                },
                timeout=10
            )

            forecast_response.raise_for_status()

            data = forecast_response.json()

            # -------------------------
            # Group by day
            # -------------------------
            daily_data = {}

            for item in data.get("list", []):

                forecast_date = datetime.utcfromtimestamp(
                    item["dt"]
                ).date()

                if not (start_date <= forecast_date <= end_date):
                    continue

                daily_data.setdefault(
                    forecast_date,
                    {
                        "temps": [],
                        "conditions": [],
                        "rain_probabilities": []
                    }
                )

                daily_data[forecast_date]["temps"].append(
                    item["main"]["temp"]
                )

                daily_data[forecast_date]["conditions"].append(
                    item["weather"][0]["description"]
                )

                daily_data[forecast_date]["rain_probabilities"].append(
                    int(item.get("pop", 0) * 100)
                )

            # -------------------------
            # Build daily summaries
            # -------------------------
            forecast_list = []

            for forecast_date in sorted(daily_data.keys()):

                day = daily_data[forecast_date]

                most_common_condition = Counter(
                    day["conditions"]
                ).most_common(1)[0][0]

                forecast_list.append({
                    "date": forecast_date.strftime("%Y-%m-%d"),
                    "temperature": round(sum(day["temps"]) / len(day["temps"])),
                    "condition": most_common_condition.capitalize(),
                    "rain_probability": max(
                        day["rain_probabilities"]
                    )
                })

            if not forecast_list:
                return {
                    "error": "No forecast data available for the selected dates"
                }, 404

            return {
                "destination": destination,
                "forecast": forecast_list
            }, 200

        except requests.exceptions.Timeout:
            return {
                "error": "Weather service timed out"
            }, 504

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Weather API error: {str(e)}"
            }, 500

        except Exception as e:
            return {
                "error": str(e)
            }, 500