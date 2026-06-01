import pytest
from services.ai_service import AIService
from unittest.mock import Mock, patch, MagicMock


class TestAIService:
    
    def test_ai_service_initialization(self):
        """Test that AIService can be initialized"""
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
            service = AIService()
            assert service is not None
            assert service.api_key == 'test_key'
            assert service.api_url == "https://openrouter.ai/api/v1/chat/completions"
            assert service.model == "nvidia/nemotron-3-super-120b-a12b:free"
    
    @patch('services.ai_service.requests.post')
    def test_generate_recommendations_success(self, mock_post):
        """Test successful recommendation generation with mocked OpenRouter API"""
        # Mock the OpenRouter response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': "Skyline Gondola\nMilford Sound Tour\nLake Wakatipu\nBen Lomond Track"
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
            service = AIService()
            result = service.generate_recommendations(
                destination="Queenstown",
                start_date="2026-07-10",
                end_date="2026-07-15",
                budget=2500,
                people=3
            )
            
            assert result["destination"] == "Queenstown"
            assert len(result["recommendations"]) == 4
            assert "Skyline Gondola" in result["recommendations"]
            assert "Milford Sound Tour" in result["recommendations"]
            # Verify the API was called with correct parameters
            mock_post.assert_called_once()
    
    @patch('services.ai_service.requests.post')
    def test_generate_recommendations_with_numbering(self, mock_post):
        """Test that recommendations are cleaned of numbering"""
        # Mock the OpenRouter response with numbered list
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': "1. Skyline Gondola\n2. Milford Sound Tour\n3. Lake Wakatipu"
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
            service = AIService()
            result = service.generate_recommendations(
                destination="Queenstown",
                start_date="2026-07-10",
                end_date="2026-07-15",
                budget=2500,
                people=3
            )
            
            assert result["destination"] == "Queenstown"
            assert "Skyline Gondola" in result["recommendations"]
            assert "Milford Sound Tour" in result["recommendations"]
            # Ensure numbering is removed
            for rec in result["recommendations"]:
                assert not rec.startswith("1.")
                assert not rec.startswith("2.")
    
    @patch('services.ai_service.requests.post')
    def test_generate_recommendations_api_failure_fallback(self, mock_post):
        """Test fallback recommendations when OpenRouter API fails"""
        # Mock requests.post to raise an exception
        mock_post.side_effect = Exception("API Error")
        
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
            service = AIService()
            result = service.generate_recommendations(
                destination="Queenstown",
                start_date="2026-07-10",
                end_date="2026-07-15",
                budget=2500,
                people=3
            )
            
            assert result["destination"] == "Queenstown"
            assert len(result["recommendations"]) > 0
            assert "Skyline Gondola" in result["recommendations"]
    
    def test_fallback_recommendations_known_destination(self):
        """Test fallback recommendations for known destinations"""
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
            service = AIService()
            result = service._get_fallback_recommendations("Queenstown")
            
            assert result["destination"] == "Queenstown"
            assert "Skyline Gondola" in result["recommendations"]
            assert "Milford Sound Tour" in result["recommendations"]
    
    def test_fallback_recommendations_unknown_destination(self):
        """Test fallback recommendations for unknown destinations"""
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
            service = AIService()
            result = service._get_fallback_recommendations("Unknown City")
            
            assert result["destination"] == "Unknown City"
            assert len(result["recommendations"]) == 4
            assert "Explore Unknown City city center" in result["recommendations"]
    
    def test_fallback_recommendations_auckland(self):
        """Test fallback recommendations for Auckland"""
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
            service = AIService()
            result = service._get_fallback_recommendations("Auckland")
            
            assert result["destination"] == "Auckland"
            assert "Sky Tower" in result["recommendations"]
            assert "Auckland War Memorial Museum" in result["recommendations"]
    
    def test_fallback_recommendations_wellington(self):
        """Test fallback recommendations for Wellington"""
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
            service = AIService()
            result = service._get_fallback_recommendations("Wellington")
            
            assert result["destination"] == "Wellington"
            assert "Te Papa Museum" in result["recommendations"]
            assert "Cable Car" in result["recommendations"]
    
    def test_fallback_recommendations_christchurch(self):
        """Test fallback recommendations for Christchurch"""
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
            service = AIService()
            result = service._get_fallback_recommendations("Christchurch")
            
            assert result["destination"] == "Christchurch"
            assert "Botanic Gardens" in result["recommendations"]
            assert "Canterbury Museum" in result["recommendations"]
