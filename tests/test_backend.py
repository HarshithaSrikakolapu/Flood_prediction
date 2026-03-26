import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app

class TestLocationPrediction(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch('httpx.AsyncClient.get')
    def test_predict_location_city_success(self, mock_get):
        # Mock OpenWeatherMap response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "London",
            "rain": {"1h": 5.0},
            "main": {"temp": 15.0, "humidity": 80}
        }
        mock_get.return_value = mock_response

        # Call endpoint with a "fake" key that is NOT the placeholder
        with patch('backend.main.OPENWEATHER_API_KEY', 'valid_looking_key'):
            response = self.client.post("/predict/location", json={"city": "London", "elevation": 10.0})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["weather_data"]["city"], "London")
        self.assertEqual(data["weather_data"]["is_demo"], False)

    def test_predict_location_demo_mode(self):
        # Test that missing/placeholder key triggers demo mode
        with patch('backend.main.OPENWEATHER_API_KEY', 'your_api_key_here'):
            response = self.client.post("/predict/location", json={"city": "London", "elevation": 10.0})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Mock City", data["weather_data"]["city"])
        self.assertEqual(data["weather_data"]["is_demo"], True)

if __name__ == '__main__':
    unittest.main()
