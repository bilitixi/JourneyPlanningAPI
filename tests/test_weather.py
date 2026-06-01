import pytest
import os
import sys
from unittest.mock import Mock, patch
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.weather_service import WeatherService


class TestWeatherService:
    """Test WeatherService functionality"""

    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key'})
    def test_weather_service_initialization(self):
        """Test that WeatherService can be initialized with API key"""
        service = WeatherService()
        assert service is not None

    @patch.dict(os.environ, {}, clear=True)
    def test_weather_service_missing_api_key(self):
        """Test that WeatherService fails without API key"""
        with pytest.raises(ValueError, match="OPENWEATHER_API_KEY not found"):
            WeatherService()

    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key'})
    @patch('services.weather_service.requests.get')
    def test_get_weather_forecast_success(self, mock_get):
        """Test successful weather forecast retrieval"""

        # FIXED: deterministic timestamp that matches date filter (2026-06-01)
        mock_timestamp = int(datetime(2026, 6, 1, tzinfo=timezone.utc).timestamp())

        # Mock geocoding response
        mock_geo = Mock()
        mock_geo.json.return_value = [{'lat': -36.84, 'lon': 174.76}]
        mock_geo.raise_for_status = Mock()

        # Mock forecast response
        mock_forecast = Mock()
        mock_forecast.json.return_value = {
            'list': [
                {
                    'dt': mock_timestamp,
                    'main': {'temp': 18.5},
                    'weather': [{'description': 'cloudy'}],
                    'pop': 0.2
                }
            ]
        }
        mock_forecast.raise_for_status = Mock()

        mock_get.side_effect = [mock_geo, mock_forecast]

        service = WeatherService()
        result, status = service.get_weather_forecast(
            destination='Auckland',
            start_date='2026-06-01',
            end_date='2026-06-05'
        )

        assert status == 200
        assert result['destination'] == 'Auckland'
        assert 'forecast' in result
        assert len(result['forecast']) > 0

    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key'})
    @patch('services.weather_service.requests.get')
    def test_get_weather_forecast_location_not_found(self, mock_get):
        """Test weather forecast with invalid location"""

        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()

        mock_get.return_value = mock_response

        service = WeatherService()
        result, status = service.get_weather_forecast(
            destination='InvalidCity',
            start_date='2026-06-01',
            end_date='2026-06-05'
        )

        assert status == 404
        assert 'error' in result
        assert 'Location not found' in result['error']


class TestWeatherEndpoint:
    """Test weather endpoint configuration"""


    def test_weather_blueprint_route_registered(self):
        from flask import Flask
        from routes.weather_routes import weather_bp

        app = Flask(__name__)
        app.register_blueprint(weather_bp)

        rules = [rule.rule for rule in app.url_map.iter_rules()]

        # verify actual route exists (correct prefix-less match)
        assert any("<journey_id>" in rule or "weather" in rule for rule in rules)


def test_ci_is_working():
    """CI smoke test"""
    assert True