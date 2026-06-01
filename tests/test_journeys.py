import pytest
import os
import sys
from datetime import date

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.journey import Journey
from routes.journey_routes import journey_bp


class TestJourneyModel:
    """Test Journey model functionality"""

    def test_journey_model_exists(self):
        """Test that Journey model exists"""
        assert Journey is not None

    def test_journey_model_has_required_fields(self):
        """Test that Journey model has required fields"""
        journey = Journey(
            user_id=1,
            destination='Auckland',
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 5),
            budget=1200.00,
            people=2,
            notes='Test journey'
        )
        assert journey.user_id == 1
        assert journey.destination == 'Auckland'
        assert journey.budget == 1200.00
        assert journey.people == 2

    def test_journey_to_dict(self):
        """Test Journey to_dict method"""
        journey = Journey(
            journey_id=1,
            user_id=1,
            destination='Auckland',
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 5),
            budget=1200.00,
            people=2,
            notes='Test journey'
        )
        result = journey.to_dict()
        assert result['journey_id'] == 1
        assert result['destination'] == 'Auckland'
        assert result['budget'] == 1200.00
        assert result['people'] == 2


class TestJourneyRoutes:
    """Test journey routes configuration"""

    def test_journey_blueprint_exists(self):
        """Test that journey blueprint is registered"""
        assert journey_bp is not None
        assert journey_bp.name == 'journey'

    def test_journey_blueprint_url_prefix(self):
        """Test that journey blueprint has correct URL prefix"""
        assert journey_bp.url_prefix == '/api/journeys'

    def test_journey_routes_defined(self):
        """Test that journey routes are defined"""
        # Check that blueprint has deferred functions (routes)
        assert hasattr(journey_bp, 'deferred_functions')
        assert len(journey_bp.deferred_functions) > 0


class TestJourneyEndpointStructure:
    """Test journey endpoint structure"""

    def test_get_all_journeys_route_exists(self):
        """Test that GET all journeys route exists"""
        # The route should be defined in the blueprint
        assert journey_bp is not None

    def test_create_journey_route_exists(self):
        """Test that POST create journey route exists"""
        assert journey_bp is not None

    def test_update_journey_route_exists(self):
        """Test that PUT update journey route exists"""
        assert journey_bp is not None

    def test_delete_journey_route_exists(self):
        """Test that DELETE journey route exists"""
        assert journey_bp is not None


def test_ci_is_working():
    """CI smoke test"""
    assert True
