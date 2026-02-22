"""
Analytics Dashboard Backend API Tests
Tests for /api/analytics/usage/ and /api/analytics/rag-performance/ endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bot-analytics-1.preview.emergentagent.com')


class TestHealthEndpoints:
    """Test basic health and status endpoints"""
    
    def test_api_health(self):
        """Test root API endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        print(f"✓ API health check passed: {data}")
    
    def test_service_status(self):
        """Test service status endpoint returns expected structure"""
        response = requests.get(f"{BASE_URL}/api/status/")
        assert response.status_code == 200
        data = response.json()
        assert 'connected' in data
        assert 'services' in data
        assert 'ollama' in data['services']
        assert 'qdrant' in data['services']
        assert 'postgresql' in data['services']
        print(f"✓ Service status: {data}")


class TestAnalyticsUsageEndpoint:
    """Test /api/analytics/usage/ endpoint"""
    
    def test_analytics_usage_returns_200(self):
        """Test analytics usage endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        assert response.status_code == 200
        print("✓ Analytics usage endpoint returns 200")
    
    def test_analytics_usage_has_summary(self):
        """Test analytics usage has summary field with required metrics"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        data = response.json()
        
        assert 'summary' in data
        summary = data['summary']
        
        # Check all required fields exist
        required_fields = [
            'total_sessions', 
            'total_messages', 
            'total_user_messages', 
            'total_bot_messages', 
            'avg_messages_per_session'
        ]
        for field in required_fields:
            assert field in summary, f"Missing field: {field}"
            assert isinstance(summary[field], (int, float)), f"Field {field} should be numeric"
        
        print(f"✓ Analytics usage summary: {summary}")
    
    def test_analytics_usage_has_feedback(self):
        """Test analytics usage has feedback distribution"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        data = response.json()
        
        assert 'feedback' in data
        feedback = data['feedback']
        
        # Check required feedback fields
        required_fields = ['helpful', 'not_helpful', 'no_feedback']
        for field in required_fields:
            assert field in feedback, f"Missing feedback field: {field}"
            assert isinstance(feedback[field], int), f"Field {field} should be integer"
        
        print(f"✓ Analytics feedback distribution: {feedback}")
    
    def test_analytics_usage_has_time_series(self):
        """Test analytics usage has time series data"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        data = response.json()
        
        # Check messages_per_day exists and is a list
        assert 'messages_per_day' in data
        assert isinstance(data['messages_per_day'], list)
        
        # Check sessions_per_day exists and is a list
        assert 'sessions_per_day' in data
        assert isinstance(data['sessions_per_day'], list)
        
        # Check messages_per_hour exists and is a list
        assert 'messages_per_hour' in data
        assert isinstance(data['messages_per_hour'], list)
        
        print("✓ Analytics usage time series fields present")


class TestAnalyticsRagPerformanceEndpoint:
    """Test /api/analytics/rag-performance/ endpoint"""
    
    def test_rag_performance_returns_200(self):
        """Test RAG performance endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/analytics/rag-performance/")
        assert response.status_code == 200
        print("✓ RAG performance endpoint returns 200")
    
    def test_rag_performance_has_summary(self):
        """Test RAG performance has summary with latency metrics"""
        response = requests.get(f"{BASE_URL}/api/analytics/rag-performance/")
        data = response.json()
        
        assert 'summary' in data
        summary = data['summary']
        
        # Check all required latency fields
        required_fields = [
            'avg_rag_latency_ms',
            'avg_llm_latency_ms',
            'avg_total_latency_ms',
            'avg_rag_score',
            'max_rag_latency_ms',
            'max_llm_latency_ms',
            'max_total_latency_ms',
            'min_rag_latency_ms',
            'min_llm_latency_ms',
            'min_total_latency_ms',
        ]
        for field in required_fields:
            assert field in summary, f"Missing field: {field}"
            assert isinstance(summary[field], (int, float)), f"Field {field} should be numeric"
        
        print(f"✓ RAG performance summary: {summary}")
    
    def test_rag_performance_has_score_distribution(self):
        """Test RAG performance has score distribution"""
        response = requests.get(f"{BASE_URL}/api/analytics/rag-performance/")
        data = response.json()
        
        assert 'score_distribution' in data
        assert isinstance(data['score_distribution'], list)
        
        # Should have 5 ranges for RAG score
        assert len(data['score_distribution']) == 5
        
        # Each item should have range and count
        for item in data['score_distribution']:
            assert 'range' in item
            assert 'count' in item
        
        print(f"✓ RAG score distribution: {data['score_distribution']}")
    
    def test_rag_performance_has_latency_distribution(self):
        """Test RAG performance has latency distribution"""
        response = requests.get(f"{BASE_URL}/api/analytics/rag-performance/")
        data = response.json()
        
        assert 'latency_distribution' in data
        assert isinstance(data['latency_distribution'], list)
        
        # Should have 5 ranges for latency
        assert len(data['latency_distribution']) == 5
        
        # Each item should have range and count
        for item in data['latency_distribution']:
            assert 'range' in item
            assert 'count' in item
        
        print(f"✓ Latency distribution: {data['latency_distribution']}")
    
    def test_rag_performance_has_recent_responses(self):
        """Test RAG performance has recent responses list"""
        response = requests.get(f"{BASE_URL}/api/analytics/rag-performance/")
        data = response.json()
        
        assert 'recent_responses' in data
        assert isinstance(data['recent_responses'], list)
        
        # If there are responses, verify structure
        if len(data['recent_responses']) > 0:
            response_item = data['recent_responses'][0]
            required_fields = [
                'id', 'timestamp', 'rag_latency_ms', 
                'llm_latency_ms', 'total_latency_ms', 'top_rag_score'
            ]
            for field in required_fields:
                assert field in response_item, f"Missing field in recent response: {field}"
        
        print(f"✓ Recent responses count: {len(data['recent_responses'])}")
    
    def test_rag_performance_has_performance_per_day(self):
        """Test RAG performance has daily performance data"""
        response = requests.get(f"{BASE_URL}/api/analytics/rag-performance/")
        data = response.json()
        
        assert 'performance_per_day' in data
        assert isinstance(data['performance_per_day'], list)
        
        # If there are entries, verify structure
        if len(data['performance_per_day']) > 0:
            day_data = data['performance_per_day'][0]
            required_fields = [
                'date', 'avg_rag_latency', 'avg_llm_latency', 
                'avg_total_latency', 'avg_rag_score', 'count'
            ]
            for field in required_fields:
                assert field in day_data, f"Missing field in performance_per_day: {field}"
        
        print(f"✓ Performance per day count: {len(data['performance_per_day'])}")


class TestChatEndpoints:
    """Test chat-related endpoints that feed analytics"""
    
    def test_sessions_list(self):
        """Test sessions list endpoint"""
        response = requests.get(f"{BASE_URL}/api/sessions/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print(f"✓ Sessions list: {len(response.json())} sessions")
    
    def test_create_session(self):
        """Test creating a new session"""
        response = requests.post(
            f"{BASE_URL}/api/sessions/",
            json={"title": "TEST_Analytics_Session"}
        )
        assert response.status_code == 201
        data = response.json()
        assert 'id' in data
        assert data['title'] == "TEST_Analytics_Session"
        
        # Clean up - delete the session
        session_id = data['id']
        delete_response = requests.delete(f"{BASE_URL}/api/sessions/{session_id}/")
        assert delete_response.status_code == 204
        
        print(f"✓ Session creation and deletion works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
