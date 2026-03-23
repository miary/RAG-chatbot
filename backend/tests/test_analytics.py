"""
Backend API Tests for RAG Chatbot Analytics Dashboard
Tests: Analytics Usage API, Analytics RAG Performance API, and core endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndStatus:
    """Health check and service status tests"""
    
    def test_health_check(self):
        """Test root health endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert 'message' in data
        print(f"✓ Health check passed: {data}")
    
    def test_service_status(self):
        """Test service status endpoint - checks Ollama, Qdrant, PostgreSQL"""
        response = requests.get(f"{BASE_URL}/api/status/")
        assert response.status_code == 200
        data = response.json()
        assert 'connected' in data
        assert 'services' in data
        assert 'ollama' in data['services']
        assert 'qdrant' in data['services']
        assert 'postgresql' in data['services']
        print(f"✓ Service status: {data}")


class TestAnalyticsUsageAPI:
    """Tests for GET /api/analytics/usage/ endpoint"""
    
    def test_usage_analytics_returns_200(self):
        """Test usage analytics endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        assert response.status_code == 200
        print("✓ Usage analytics endpoint returns 200")
    
    def test_usage_analytics_summary_structure(self):
        """Test usage analytics has correct summary structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        data = response.json()
        
        assert 'summary' in data
        summary = data['summary']
        
        # Verify all required summary fields
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
        
        print(f"✓ Usage summary structure valid: {summary}")
    
    def test_usage_analytics_messages_over_time(self):
        """Test messages_over_time array structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        data = response.json()
        
        assert 'messages_over_time' in data
        assert isinstance(data['messages_over_time'], list)
        
        if len(data['messages_over_time']) > 0:
            item = data['messages_over_time'][0]
            assert 'date' in item
            assert 'user_count' in item
            assert 'bot_count' in item
            assert 'total' in item
            print(f"✓ Messages over time structure valid: {item}")
        else:
            print("✓ Messages over time is empty (no data yet)")
    
    def test_usage_analytics_sessions_over_time(self):
        """Test sessions_over_time array structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        data = response.json()
        
        assert 'sessions_over_time' in data
        assert isinstance(data['sessions_over_time'], list)
        
        if len(data['sessions_over_time']) > 0:
            item = data['sessions_over_time'][0]
            assert 'date' in item
            assert 'count' in item
            print(f"✓ Sessions over time structure valid: {item}")
        else:
            print("✓ Sessions over time is empty (no data yet)")
    
    def test_usage_analytics_feedback_distribution(self):
        """Test feedback_distribution structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        data = response.json()
        
        assert 'feedback_distribution' in data
        feedback = data['feedback_distribution']
        
        assert 'thumbs_up' in feedback
        assert 'thumbs_down' in feedback
        assert 'no_feedback' in feedback
        
        # All should be non-negative integers
        assert feedback['thumbs_up'] >= 0
        assert feedback['thumbs_down'] >= 0
        assert feedback['no_feedback'] >= 0
        
        print(f"✓ Feedback distribution valid: {feedback}")


class TestAnalyticsRAGPerformanceAPI:
    """Tests for GET /api/analytics/rag/ endpoint"""
    
    def test_rag_analytics_returns_200(self):
        """Test RAG analytics endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/analytics/rag/")
        assert response.status_code == 200
        print("✓ RAG analytics endpoint returns 200")
    
    def test_rag_analytics_summary_structure(self):
        """Test RAG analytics has correct summary structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/rag/")
        data = response.json()
        
        assert 'summary' in data
        summary = data['summary']
        
        # Verify all required summary fields
        required_fields = [
            'total_responses',
            'avg_rag_latency_ms',
            'avg_llm_latency_ms',
            'avg_total_latency_ms',
            'avg_rag_score',
            'max_rag_latency_ms',
            'max_llm_latency_ms',
            'min_rag_latency_ms',
            'min_llm_latency_ms',
            'max_rag_score',
            'min_rag_score'
        ]
        for field in required_fields:
            assert field in summary, f"Missing field: {field}"
        
        print(f"✓ RAG summary structure valid: {summary}")
    
    def test_rag_analytics_latency_over_time(self):
        """Test latency_over_time array structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/rag/")
        data = response.json()
        
        assert 'latency_over_time' in data
        assert isinstance(data['latency_over_time'], list)
        
        if len(data['latency_over_time']) > 0:
            item = data['latency_over_time'][0]
            assert 'date' in item
            assert 'avg_rag_ms' in item
            assert 'avg_llm_ms' in item
            assert 'avg_total_ms' in item
            assert 'avg_score' in item
            assert 'count' in item
            print(f"✓ Latency over time structure valid: {item}")
        else:
            print("✓ Latency over time is empty (no data yet)")
    
    def test_rag_analytics_score_distribution(self):
        """Test score_distribution structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/rag/")
        data = response.json()
        
        assert 'score_distribution' in data
        scores = data['score_distribution']
        
        required_buckets = ['excellent', 'good', 'fair', 'poor']
        for bucket in required_buckets:
            assert bucket in scores, f"Missing bucket: {bucket}"
            assert scores[bucket] >= 0
        
        print(f"✓ Score distribution valid: {scores}")
    
    def test_rag_analytics_latency_distribution(self):
        """Test latency_distribution structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/rag/")
        data = response.json()
        
        assert 'latency_distribution' in data
        latency = data['latency_distribution']
        
        required_buckets = ['fast', 'normal', 'slow', 'very_slow']
        for bucket in required_buckets:
            assert bucket in latency, f"Missing bucket: {bucket}"
            assert latency[bucket] >= 0
        
        print(f"✓ Latency distribution valid: {latency}")


class TestSessionsAPI:
    """Tests for sessions endpoints"""
    
    def test_list_sessions(self):
        """Test GET /api/sessions/ returns list"""
        response = requests.get(f"{BASE_URL}/api/sessions/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Sessions list returned {len(data)} sessions")
    
    def test_create_session(self):
        """Test POST /api/sessions/ creates new session"""
        response = requests.post(f"{BASE_URL}/api/sessions/", json={
            "title": "TEST_session_for_testing"
        })
        assert response.status_code == 201
        data = response.json()
        assert 'id' in data
        assert data['title'] == "TEST_session_for_testing"
        print(f"✓ Session created: {data['id']}")
        return data['id']
    
    def test_get_session_detail(self):
        """Test GET /api/sessions/<id>/ returns session details"""
        # First create a session
        create_response = requests.post(f"{BASE_URL}/api/sessions/", json={
            "title": "TEST_detail_session"
        })
        session_id = create_response.json()['id']
        
        # Then get its details
        response = requests.get(f"{BASE_URL}/api/sessions/{session_id}/")
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == session_id
        assert 'messages' in data
        print(f"✓ Session detail retrieved: {data['id']}")
    
    def test_delete_session(self):
        """Test DELETE /api/sessions/<id>/ deletes session"""
        # First create a session
        create_response = requests.post(f"{BASE_URL}/api/sessions/", json={
            "title": "TEST_delete_session"
        })
        session_id = create_response.json()['id']
        
        # Then delete it
        response = requests.delete(f"{BASE_URL}/api/sessions/{session_id}/")
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = requests.get(f"{BASE_URL}/api/sessions/{session_id}/")
        assert get_response.status_code == 404
        print(f"✓ Session deleted successfully")


class TestRemoteQdrantConnection:
    """Tests for remote Qdrant connection at 148.230.92.74:6333"""
    
    def test_qdrant_connected_via_status(self):
        """Verify Qdrant is connected via status endpoint"""
        response = requests.get(f"{BASE_URL}/api/status/")
        data = response.json()
        assert data['services']['qdrant'] == True, "Qdrant should be connected"
        print("✓ Qdrant is connected via status endpoint")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
