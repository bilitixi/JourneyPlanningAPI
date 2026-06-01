import pytest
import os
import sys
from datetime import date

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models.journey import Journey
from models.user import User
from db import Base, engine, SessionLocal
import jwt


# =========================
# FIXTURES
# =========================
@pytest.fixture(scope='function')
def db_session():
    """Create a clean test database session."""
    from sqlalchemy import text
    
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    return app.test_client()


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
    return jwt.encode(payload, secret, algorithm='HS256')


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


# =========================
# TEST JOURNEY ENDPOINTS
# =========================
class TestJourneyRoutes:
    """Tests for journey routes."""

    def test_get_all_journeys_success(self, client, sample_journey, auth_token):
        """Test getting all journeys for authenticated user."""
        response = client.get(
            '/api/journeys',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'journeys' in data
        assert len(data['journeys']) == 1
        assert data['journeys'][0]['destination'] == 'Auckland'

    def test_get_all_journeys_unauthorized(self, client):
        """Test getting journeys without authentication."""
        response = client.get('/api/journeys')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_get_all_journeys_empty(self, client, sample_user, auth_token):
        """Test getting journeys when user has no journeys."""
        response = client.get(
            '/api/journeys',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'journeys' in data
        assert len(data['journeys']) == 0

    def test_get_journey_by_id_success(self, client, sample_journey, auth_token):
        """Test getting a specific journey by ID."""
        response = client.get(
            f'/api/journeys/{sample_journey.journey_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['destination'] == 'Auckland'
        assert data['budget'] == 1200.0

    def test_get_journey_by_id_not_found(self, client, auth_token):
        """Test getting a non-existent journey."""
        response = client.get(
            '/api/journeys/99999',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Journey not found' in data['error']

    def test_get_journey_by_id_unauthorized(self, client, sample_journey):
        """Test getting journey without authentication."""
        response = client.get(f'/api/journeys/{sample_journey.journey_id}')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_create_journey_success(self, client, auth_token):
        """Test creating a new journey."""
        journey_data = {
            'destination': 'Queenstown',
            'start_date': '2026-07-10',
            'end_date': '2026-07-15',
            'budget': 2500,
            'people': 3,
            'notes': 'Winter holiday'
        }
        
        response = client.post(
            '/api/journeys',
            headers={'Authorization': f'Bearer {auth_token}'},
            json=journey_data
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['destination'] == 'Queenstown'
        assert data['budget'] == 2500
        assert 'journey_id' in data

    def test_create_journey_missing_field(self, client, auth_token):
        """Test creating journey with missing required field."""
        journey_data = {
            'destination': 'Queenstown',
            'start_date': '2026-07-10',
            'end_date': '2026-07-15',
            'budget': 2500
            # Missing 'people' field
        }
        
        response = client.post(
            '/api/journeys',
            headers={'Authorization': f'Bearer {auth_token}'},
            json=journey_data
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Missing required field' in data['error']

    def test_create_journey_invalid_date_format(self, client, auth_token):
        """Test creating journey with invalid date format."""
        journey_data = {
            'destination': 'Queenstown',
            'start_date': '10/07/2026',  # Invalid format
            'end_date': '2026-07-15',
            'budget': 2500,
            'people': 3
        }
        
        response = client.post(
            '/api/journeys',
            headers={'Authorization': f'Bearer {auth_token}'},
            json=journey_data
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid date format' in data['error']

    def test_create_journey_unauthorized(self, client):
        """Test creating journey without authentication."""
        journey_data = {
            'destination': 'Queenstown',
            'start_date': '2026-07-10',
            'end_date': '2026-07-15',
            'budget': 2500,
            'people': 3
        }
        
        response = client.post('/api/journeys', json=journey_data)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_update_journey_success(self, client, sample_journey, auth_token):
        """Test updating an existing journey."""
        update_data = {
            'destination': 'Wellington',
            'budget': 3000
        }
        
        response = client.put(
            f'/api/journeys/{sample_journey.journey_id}',
            headers={'Authorization': f'Bearer {auth_token}'},
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['destination'] == 'Wellington'
        assert data['budget'] == 3000

    def test_update_journey_not_found(self, client, auth_token):
        """Test updating a non-existent journey."""
        update_data = {'destination': 'Wellington'}
        
        response = client.put(
            '/api/journeys/99999',
            headers={'Authorization': f'Bearer {auth_token}'},
            json=update_data
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Journey not found' in data['error']

    def test_update_journey_invalid_date_format(self, client, sample_journey, auth_token):
        """Test updating journey with invalid date format."""
        update_data = {
            'start_date': '10/07/2026'  # Invalid format
        }
        
        response = client.put(
            f'/api/journeys/{sample_journey.journey_id}',
            headers={'Authorization': f'Bearer {auth_token}'},
            json=update_data
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid date format' in data['error']

    def test_update_journey_unauthorized(self, client, sample_journey):
        """Test updating journey without authentication."""
        update_data = {'destination': 'Wellington'}
        
        response = client.put(
            f'/api/journeys/{sample_journey.journey_id}',
            json=update_data
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_delete_journey_success(self, client, sample_journey, auth_token):
        """Test deleting a journey."""
        response = client.delete(
            f'/api/journeys/{sample_journey.journey_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'deleted successfully' in data['message']

    def test_delete_journey_not_found(self, client, auth_token):
        """Test deleting a non-existent journey."""
        response = client.delete(
            '/api/journeys/99999',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Journey not found' in data['error']

    def test_delete_journey_unauthorized(self, client, sample_journey):
        """Test deleting journey without authentication."""
        response = client.delete(f'/api/journeys/{sample_journey.journey_id}')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data


# =========================
# CI SMOKE TEST
# =========================
def test_ci_is_working():
    """CI smoke test"""
    assert True
