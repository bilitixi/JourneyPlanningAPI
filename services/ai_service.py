import os
import requests
import json
from datetime import datetime


class AIService:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "nvidia/nemotron-3-super-120b-a12b:free"
    
    def generate_recommendations(self, destination, start_date, end_date, budget, people):
        """
        Generate travel recommendations using OpenRouter API with NVIDIA Nemotron model based on journey details.
        
        Args:
            destination (str): Travel destination
            start_date (str): Journey start date (YYYY-MM-DD)
            end_date (str): Journey end date (YYYY-MM-DD)
            budget (float): Travel budget
            people (int): Number of travelers
        
        Returns:
            dict: Dictionary containing destination and list of recommendations
        """
        try:
            # Calculate trip duration
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            duration = (end - start).days + 1
            
            # Create prompt for the model
            prompt = f"""
            Generate 4-6 travel recommendations for {destination}.
            
            Trip details:
            - Destination: {destination}
            - Duration: {duration} days ({start_date} to {end_date})
            - Budget: ${budget}
            - Number of travelers: {people}
            
            Provide specific attractions, activities, or experiences that are suitable for this destination and budget.
            Return only the recommendations as a comma-separated list, with each recommendation on a new line.
            """
            
            # Call OpenRouter API
            response = requests.post(
                url=self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a travel recommendation assistant. Provide specific, practical travel recommendations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "reasoning": {"enabled": True}
                })
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            # Parse recommendations from response
            recommendations_text = response_data['choices'][0]['message']['content'].strip()
            recommendations = [rec.strip() for rec in recommendations_text.split('\n') if rec.strip()]
            
            # Clean up recommendations (remove numbering if present)
            cleaned_recommendations = []
            for rec in recommendations:
                # Remove any leading numbers or bullets
                cleaned = rec.lstrip('0123456789.-* ')
                if cleaned:
                    cleaned_recommendations.append(cleaned)
            
            return {
                "destination": destination,
                "recommendations": cleaned_recommendations[:6]  # Limit to 6 recommendations
            }
            
        except Exception as e:
            # Fallback to mock recommendations if API fails
            return self._get_fallback_recommendations(destination)
    
    def _get_fallback_recommendations(self, destination):
        """
        Provide fallback recommendations when OpenAI API is unavailable.
        
        Args:
            destination (str): Travel destination
        
        Returns:
            dict: Dictionary containing destination and fallback recommendations
        """
        fallback_recommendations = {
            "Queenstown": [
                "Skyline Gondola",
                "Milford Sound Tour",
                "Lake Wakatipu",
                "Ben Lomond Track"
            ],
            "Auckland": [
                "Sky Tower",
                "Auckland War Memorial Museum",
                "Viaduct Harbour",
                "Mount Eden"
            ],
            "Wellington": [
                "Te Papa Museum",
                "Cable Car",
                "Zealandia",
                "Weta Workshop"
            ],
            "Christchurch": [
                "Botanic Gardens",
                "Canterbury Museum",
                "International Antarctic Centre",
                "Cashel Street"
            ]
        }
        
        recommendations = fallback_recommendations.get(destination, [
            f"Explore {destination} city center",
            "Visit local museums",
            "Try local cuisine",
            "Walk through parks"
        ])
        
        return {
            "destination": destination,
            "recommendations": recommendations
        }
