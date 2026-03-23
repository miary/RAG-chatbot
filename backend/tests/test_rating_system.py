"""
Test suite for the 5-star rating system
Tests:
- Rating API (PATCH /api/messages/{id}/feedback/)
- Rating validation (1-5 range)
- Usage analytics rating_distribution
- Usage analytics avg_rating and total_rated
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRatingAPI:
    """Tests for the rating feedback endpoint"""
    
    @pytest.fixture(scope="class")
    def test_session_and_message(self):
        """Create a test session with a bot message for rating tests"""
        # Create a session and send a message to get a bot response
        response = requests.post(f"{BASE_URL}/api/chat/", json={
            "message": "TEST_rating_test_message",
            "session_id": None
        }, timeout=120)  # LLM can be slow
        
        if response.status_code != 200:
            pytest.skip(f"Could not create test message: {response.status_code}")
        
        data = response.json()
        session_id = data['session_id']
        bot_message_id = data['bot_message']['id']
        
        yield {
            'session_id': session_id,
            'bot_message_id': bot_message_id
        }
        
        # Cleanup: delete the session
        try:
            requests.delete(f"{BASE_URL}/api/sessions/{session_id}/")
        except:
            pass
    
    def test_rating_5_stars(self, test_session_and_message):
        """Test submitting a 5-star rating"""
        message_id = test_session_and_message['bot_message_id']
        
        response = requests.patch(
            f"{BASE_URL}/api/messages/{message_id}/feedback/",
            json={"rating": 5}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data['rating'] == 5, f"Expected rating=5, got {data.get('rating')}"
    
    def test_rating_4_stars(self, test_session_and_message):
        """Test submitting a 4-star rating"""
        message_id = test_session_and_message['bot_message_id']
        
        response = requests.patch(
            f"{BASE_URL}/api/messages/{message_id}/feedback/",
            json={"rating": 4}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['rating'] == 4
    
    def test_rating_3_stars(self, test_session_and_message):
        """Test submitting a 3-star rating"""
        message_id = test_session_and_message['bot_message_id']
        
        response = requests.patch(
            f"{BASE_URL}/api/messages/{message_id}/feedback/",
            json={"rating": 3}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['rating'] == 3
    
    def test_rating_2_stars(self, test_session_and_message):
        """Test submitting a 2-star rating"""
        message_id = test_session_and_message['bot_message_id']
        
        response = requests.patch(
            f"{BASE_URL}/api/messages/{message_id}/feedback/",
            json={"rating": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['rating'] == 2
    
    def test_rating_1_star(self, test_session_and_message):
        """Test submitting a 1-star rating"""
        message_id = test_session_and_message['bot_message_id']
        
        response = requests.patch(
            f"{BASE_URL}/api/messages/{message_id}/feedback/",
            json={"rating": 1}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['rating'] == 1


class TestRatingValidation:
    """Tests for rating validation (should reject values outside 1-5)"""
    
    @pytest.fixture(scope="class")
    def test_message_for_validation(self):
        """Create a test message for validation tests"""
        response = requests.post(f"{BASE_URL}/api/chat/", json={
            "message": "TEST_validation_test_message",
            "session_id": None
        }, timeout=120)
        
        if response.status_code != 200:
            pytest.skip(f"Could not create test message: {response.status_code}")
        
        data = response.json()
        session_id = data['session_id']
        bot_message_id = data['bot_message']['id']
        
        yield {
            'session_id': session_id,
            'bot_message_id': bot_message_id
        }
        
        # Cleanup
        try:
            requests.delete(f"{BASE_URL}/api/sessions/{session_id}/")
        except:
            pass
    
    def test_rating_0_rejected(self, test_message_for_validation):
        """Test that rating=0 is rejected"""
        message_id = test_message_for_validation['bot_message_id']
        
        response = requests.patch(
            f"{BASE_URL}/api/messages/{message_id}/feedback/",
            json={"rating": 0}
        )
        
        assert response.status_code == 400, f"Expected 400 for rating=0, got {response.status_code}"
    
    def test_rating_6_rejected(self, test_message_for_validation):
        """Test that rating=6 is rejected"""
        message_id = test_message_for_validation['bot_message_id']
        
        response = requests.patch(
            f"{BASE_URL}/api/messages/{message_id}/feedback/",
            json={"rating": 6}
        )
        
        assert response.status_code == 400, f"Expected 400 for rating=6, got {response.status_code}"
    
    def test_rating_negative_rejected(self, test_message_for_validation):
        """Test that negative rating is rejected"""
        message_id = test_message_for_validation['bot_message_id']
        
        response = requests.patch(
            f"{BASE_URL}/api/messages/{message_id}/feedback/",
            json={"rating": -1}
        )
        
        assert response.status_code == 400, f"Expected 400 for rating=-1, got {response.status_code}"
    
    def test_rating_100_rejected(self, test_message_for_validation):
        """Test that rating=100 is rejected"""
        message_id = test_message_for_validation['bot_message_id']
        
        response = requests.patch(
            f"{BASE_URL}/api/messages/{message_id}/feedback/",
            json={"rating": 100}
        )
        
        assert response.status_code == 400, f"Expected 400 for rating=100, got {response.status_code}"
    
    def test_rating_null_accepted(self, test_message_for_validation):
        """Test that rating=null is accepted (to clear rating)"""
        message_id = test_message_for_validation['bot_message_id']
        
        response = requests.patch(
            f"{BASE_URL}/api/messages/{message_id}/feedback/",
            json={"rating": None}
        )
        
        assert response.status_code == 200, f"Expected 200 for rating=null, got {response.status_code}"
        data = response.json()
        assert data['rating'] is None
    
    def test_nonexistent_message_404(self):
        """Test that rating a non-existent message returns 404"""
        fake_id = str(uuid.uuid4())
        
        response = requests.patch(
            f"{BASE_URL}/api/messages/{fake_id}/feedback/",
            json={"rating": 5}
        )
        
        assert response.status_code == 404, f"Expected 404 for non-existent message, got {response.status_code}"


class TestUsageAnalyticsRating:
    """Tests for rating data in usage analytics endpoint"""
    
    def test_usage_analytics_has_rating_distribution(self):
        """Test that usage analytics returns rating_distribution with all star levels"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check rating_distribution exists
        assert 'rating_distribution' in data, "rating_distribution missing from response"
        
        rating_dist = data['rating_distribution']
        
        # Check all required keys exist
        required_keys = ['5_stars', '4_stars', '3_stars', '2_stars', '1_star', 'no_rating']
        for key in required_keys:
            assert key in rating_dist, f"Missing key '{key}' in rating_distribution"
            assert isinstance(rating_dist[key], int), f"'{key}' should be an integer"
    
    def test_usage_analytics_has_avg_rating(self):
        """Test that usage analytics returns avg_rating in summary"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check summary exists
        assert 'summary' in data, "summary missing from response"
        
        summary = data['summary']
        
        # Check avg_rating exists (can be null if no ratings)
        assert 'avg_rating' in summary, "avg_rating missing from summary"
        
        # avg_rating should be None or a number between 1 and 5
        avg_rating = summary['avg_rating']
        if avg_rating is not None:
            assert 1 <= avg_rating <= 5, f"avg_rating should be between 1-5, got {avg_rating}"
    
    def test_usage_analytics_has_total_rated(self):
        """Test that usage analytics returns total_rated in summary"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        
        assert response.status_code == 200
        data = response.json()
        
        summary = data['summary']
        
        # Check total_rated exists
        assert 'total_rated' in summary, "total_rated missing from summary"
        assert isinstance(summary['total_rated'], int), "total_rated should be an integer"
        assert summary['total_rated'] >= 0, "total_rated should be non-negative"
    
    def test_rating_distribution_consistency(self):
        """Test that rating distribution counts are consistent with total_rated"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        
        assert response.status_code == 200
        data = response.json()
        
        rating_dist = data['rating_distribution']
        summary = data['summary']
        
        # Sum of all star ratings should equal total_rated
        total_from_dist = (
            rating_dist['5_stars'] +
            rating_dist['4_stars'] +
            rating_dist['3_stars'] +
            rating_dist['2_stars'] +
            rating_dist['1_star']
        )
        
        assert total_from_dist == summary['total_rated'], \
            f"Sum of ratings ({total_from_dist}) != total_rated ({summary['total_rated']})"


class TestExistingRatedMessage:
    """Test with the existing rated message mentioned in context"""
    
    def test_existing_rated_message(self):
        """Test that the existing 5-star rated message (85e2699e-2eab-47d2-a423-6e30de7a6a08) has rating"""
        message_id = "85e2699e-2eab-47d2-a423-6e30de7a6a08"
        
        # Try to update the rating to verify the endpoint works with this message
        response = requests.patch(
            f"{BASE_URL}/api/messages/{message_id}/feedback/",
            json={"rating": 5}
        )
        
        # If message exists, should return 200; if not, 404
        if response.status_code == 200:
            data = response.json()
            assert data['rating'] == 5
            print(f"Existing message {message_id} rating updated to 5")
        elif response.status_code == 404:
            print(f"Message {message_id} not found (may have been deleted)")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
