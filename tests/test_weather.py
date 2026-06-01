import pytest
from unittest.mock import Mock, patch
from datetime import date
from app import app
from models.journey import Journey
from models.user import User
from db import Base, engine, SessionLocal
import jwt
import os


# =========================
# FIXED DB SETUP (FRESH DB SAFE)
# =========================
@pytest.fixture(scope='session', autouse=True)
def setup_database():
    """
    Runs ONCE for CI fresh DB.
    Creates all tables safely.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def db_session():
    """Transaction-based test isolation (no drop_all needed)."""

    connection = engine.connect()
    transaction = connection.begin()

    session = SessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# =========================
# FLASK CLIENT
# =========================
@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()


# =========================
# JWT FIX
# =========================
@pytest.fixture
def auth_token():
    payload = {
        'user_id': 1,
        'email': 'test@example.com',
        'role': 'user',
        'exp': 9999999999,
        'iat': 1234567890
    }

    secret = os.getenv('JWT_SECRET_KEY', 'test-secret-key')
    return jwt.encode(payload, secret, algorithm='HS256')


# =========================
# SAMPLE DATA FIX
# =========================
@pytest.fixture
def sample_user(db_session):
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


# =========================
# WEATHER SERVICE TESTS
# =========================
class TestWeatherService:

    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key'})
    @patch('services.weather_service.requests.get')
    def test_success(self, mock_get):
        from services.weather_service import WeatherService

        mock_geo = Mock()
        mock_geo.json.return_value = [{'lat': -36.84, 'lon': 174.76}]
        mock_geo.raise_for_status = Mock()

        mock_forecast = Mock()
        mock_forecast.json.return_value = {
            'list': [
                {
                    'dt': 1748736000,
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


    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self):
        from services.weather_service import WeatherService

        with pytest.raises(ValueError):
            WeatherService()


# =========================
# ROUTE TESTS
# =========================
class TestWeatherRoutes:

    @patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test-api-key'})
    @patch('services.weather_service.requests.get')
    def test_route_success(self, mock_get, client, sample_journey, auth_token):

        mock_geo = Mock()
        mock_geo.json.return_value = [{'lat': -36.84, 'lon': 174.76}]
        mock_geo.raise_for_status = Mock()

        mock_forecast = Mock()
        mock_forecast.json.return_value = {
            'list': [
                {
                    'dt': 1748736000,
                    'main': {'temp': 18.5},
                    'weather': [{'description': 'cloudy'}],
                    'pop': 0.2
                }
            ]
        }
        mock_forecast.raise_for_status = Mock()

        mock_get.side_effect = [mock_geo, mock_forecast]

        response = client.get(
            f'/api/weather/{sample_journey.id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200


    def test_unauthorized(self, client, sample_journey):
        response = client.get(f'/api/weather/{sample_journey.id}')
        assert response.status_code == 401


    def test_not_found(self, client, auth_token):
        response = client.get(
            '/api/weather/99999',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 404


# =========================
# CI SMOKE TEST
# =========================
def test_ci_is_working():
    assert True