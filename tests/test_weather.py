import pytest
from unittest.mock import Mock, patch
from datetime import date
from app import app
from models.journey import Journey
from models.user import User
from db import Base, engine, SessionLocal, init_db
import jwt
import os


@pytest.fixture(scope='function')
def db_session():
    """Create a test database session."""
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_token():
    """Create a valid JWT token for testing."""
    payload = {
        'user_id': 1,
        'email': 'test@example.com',
        'role': 'user',
        'exp': 9999999999,
        'iat': 1234567890
    }
    secret = os.getenv('JWT_SECRET_KEY', 'test-secret-key')
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        first_name='Test',
        last_name='User',
        email='test@example.com',
        password_hash='hashed_password',
        role='user'
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_journey(db_session, sample_user):
    """Create a sample journey for testing."""
    journey = Journey(
        user_id=sample_user.id,
        destination='Auckland',
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 5),
        budget=1200.00,
        people=2,
        notes='Test journey'
    )
    db_session.add(journey)
    db_session.commit()
    db_session.refresh(journey)
    return journey


class TestWeatherService:
    """Tests for WeatherService."""
    
    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key'})
    @patch('services.weather_service.requests.get')
    def test_get_weather_forecast_success(self, mock_get):
        """Test successful weather forecast retrieval."""
        from services.weather_service import WeatherService
        
        # Mock geocoding response
        mock_geocoding_response = Mock()
        mock_geocoding_response.json.return_value = [
            {'lat': -36.8485, 'lon': 174.7633}
        ]
        mock_geocoding_response.raise_for_status = Mock()
        
        # Mock forecast response
        mock_forecast_response = Mock()
        mock_forecast_response.json.return_value = {
            'list': [
                {
                    'dt': 1748736000,  # 2026-06-01
                    'main': {'temp': 18.5},
                    'weather': [{'description': 'cloudy'}],
                    'pop': 0.2
                },
                {
                    'dt': 1748822400,  # 2026-06-02
                    'main': {'temp': 19.0},
                    'weather': [{'description': 'sunny'}],
                    'pop': 0.0
                }
            ]
        }
        mock_forecast_response.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_geocoding_response, mock_forecast_response]
        
        service = WeatherService()
        result, status_code = service.get_weather_forecast(
            destination='Auckland',
            start_date='2026-06-01',
            end_date='2026-06-05'
        )
        
        assert status_code == 200
        assert result['destination'] == 'Auckland'
        assert len(result['forecast']) == 2
        assert result['forecast'][0]['date'] == '2026-06-01'
        assert result['forecast'][0]['temperature'] == 18
        assert result['forecast'][0]['condition'] == 'Cloudy'
        assert result['forecast'][0]['rain_probability'] == 20
    
    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key'})
    @patch('services.weather_service.requests.get')
    def test_get_weather_forecast_location_not_found(self, mock_get):
        """Test weather forecast with invalid location."""
        from services.weather_service import WeatherService
        
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        
        mock_get.return_value = mock_response
        
        service = WeatherService()
        result, status_code = service.get_weather_forecast(
            destination='InvalidCity',
            start_date='2026-06-01',
            end_date='2026-06-05'
        )
        
        assert status_code == 404
        assert 'error' in result
        assert 'Location not found' in result['error']
    
    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key'})
    @patch('services.weather_service.requests.get')
    def test_get_weather_forecast_no_forecast_data(self, mock_get):
        """Test weather forecast when no data available for dates."""
        from services.weather_service import WeatherService
        
        # Mock geocoding response
        mock_geocoding_response = Mock()
        mock_geocoding_response.json.return_value = [
            {'lat': -36.8485, 'lon': 174.7633}
        ]
        mock_geocoding_response.raise_for_status = Mock()
        
        # Mock forecast response with dates outside range
        mock_forecast_response = Mock()
        mock_forecast_response.json.return_value = {
            'list': [
                {
                    'dt': 1748208000,  # 2026-05-26 (outside range)
                    'main': {'temp': 15.0},
                    'weather': [{'description': 'rainy'}],
                    'pop': 0.8
                }
            ]
        }
        mock_forecast_response.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_geocoding_response, mock_forecast_response]
        
        service = WeatherService()
        result, status_code = service.get_weather_forecast(
            destination='Auckland',
            start_date='2026-06-01',
            end_date='2026-06-05'
        )
        
        assert status_code == 404
        assert 'error' in result
        assert 'No forecast data available' in result['error']
    
    @patch.dict(os.environ, {}, clear=True)
    def test_weather_service_missing_api_key(self):
        """Test WeatherService initialization without API key."""
        from services.weather_service import WeatherService
        
        with pytest.raises(ValueError, match="OPENWEATHER_API_KEY not found"):
            WeatherService()


class TestWeatherRoutes:
    """Tests for weather routes."""
    
    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key'})
    @patch('services.weather_service.requests.get')
    def test_get_weather_forecast_success(self, mock_get, client, sample_journey, auth_token):
        """Test successful weather forecast retrieval via route."""
        # Mock geocoding response
        mock_geocoding_response = Mock()
        mock_geocoding_response.json.return_value = [
            {'lat': -36.8485, 'lon': 174.7633}
        ]
        mock_geocoding_response.raise_for_status = Mock()
        
        # Mock forecast response
        mock_forecast_response = Mock()
        mock_forecast_response.json.return_value = {
            'list': [
                {
                    'dt': 1748736000,
                    'main': {'temp': 18.5},
                    'weather': [{'description': 'cloudy'}],
                    'pop': 0.2
                }
            ]
        }
        mock_forecast_response.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_geocoding_response, mock_forecast_response]
        
        response = client.get(
            f'/api/weather/{sample_journey.journey_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['destination'] == 'Auckland'
        assert len(data['forecast']) == 1
    
    def test_get_weather_forecast_unauthorized(self, client, sample_journey):
        """Test weather forecast without authentication."""
        response = client.get(f'/api/weather/{sample_journey.journey_id}')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_get_weather_forecast_journey_not_found(self, client, auth_token):
        """Test weather forecast for non-existent journey."""
        response = client.get(
            '/api/weather/99999',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Journey not found' in data['error']
    
    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key'})
    @patch('services.weather_service.WeatherService.get_weather_forecast')
    def test_get_weather_forecast_service_error(self, mock_get_forecast, client, sample_journey, auth_token):
        """Test weather forecast when service returns error."""
        mock_get_forecast.return_value = (
            {'error': 'Failed to fetch weather data'},
            500
        )
        
        response = client.get(
            f'/api/weather/{sample_journey.journey_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data


def test_ci_is_working():
    """Basic test to verify CI pipeline is functioning."""
    assert True
