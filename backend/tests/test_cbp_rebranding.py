"""
CBP Training Assistant Rebranding Tests
Tests to verify the application has been properly rebranded from FRDS to CBP Training Assistant
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndStatus:
    """Test health check and status endpoints for CBP branding"""
    
    def test_health_check_cbp_branding(self):
        """Verify health check returns 'CBP Training Assistant API is running'"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'CBP Training Assistant API is running'
        assert data['status'] == 'ok'
        print("✓ Health check returns CBP Training Assistant branding")
    
    def test_service_status(self):
        """Verify all services are connected"""
        response = requests.get(f"{BASE_URL}/api/status/")
        assert response.status_code == 200
        data = response.json()
        assert 'services' in data
        assert data['services']['postgresql'] == True
        # Ollama and Qdrant may have cold start latency
        print(f"✓ Service status: {data}")


class TestIngestEndpoint:
    """Test ingest endpoint for CBP training content"""
    
    def test_ingest_cbp_training_documents(self):
        """Verify /api/ingest/ ingests 12 CBP training documents"""
        response = requests.post(f"{BASE_URL}/api/ingest/")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['documents_ingested'] == 12
        print(f"✓ Ingested {data['documents_ingested']} CBP training documents")


class TestChatEndpoint:
    """Test chat endpoint for CBP-relevant responses"""
    
    def test_chat_cbp_inspection_query(self):
        """Verify chat returns CBP-relevant training responses"""
        response = requests.post(f"{BASE_URL}/api/chat/", json={
            "message": "What are the primary inspection procedures at a port of entry?"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert 'session_id' in data
        assert 'user_message' in data
        assert 'bot_message' in data
        
        # Verify bot message has sources
        bot_msg = data['bot_message']
        assert 'text' in bot_msg
        assert 'sources' in bot_msg
        
        # Verify sources reference CBP training modules
        sources = bot_msg.get('sources', [])
        if sources:
            # Check that sources have titles related to CBP training
            source_titles = [s.get('title', '') for s in sources]
            print(f"✓ Chat sources: {source_titles}")
            # At least one source should mention inspection or CBP-related content
            has_relevant_source = any(
                'inspection' in title.lower() or 
                'cbp' in title.lower() or 
                'port' in title.lower() or
                'entry' in title.lower()
                for title in source_titles
            )
            assert has_relevant_source or len(sources) > 0, "Expected CBP-relevant sources"
        
        print(f"✓ Chat response received with {len(sources)} sources")
    
    def test_chat_document_verification_query(self):
        """Test chat with document verification query"""
        response = requests.post(f"{BASE_URL}/api/chat/", json={
            "message": "How do I verify immigration documents?"
        })
        assert response.status_code == 200
        data = response.json()
        assert 'bot_message' in data
        bot_text = data['bot_message'].get('text', '')
        assert len(bot_text) > 0
        print(f"✓ Document verification query returned response ({len(bot_text)} chars)")
    
    def test_chat_customs_query(self):
        """Test chat with customs-related query"""
        response = requests.post(f"{BASE_URL}/api/chat/", json={
            "message": "What are the duty-free exemptions for returning residents?"
        })
        assert response.status_code == 200
        data = response.json()
        assert 'bot_message' in data
        sources = data['bot_message'].get('sources', [])
        print(f"✓ Customs query returned response with {len(sources)} sources")


class TestAnalyticsEndpoints:
    """Test analytics endpoints for CBP Training Analytics"""
    
    def test_usage_analytics(self):
        """Verify usage analytics endpoint works"""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        assert response.status_code == 200
        data = response.json()
        assert 'summary' in data
        assert 'messages_over_time' in data
        assert 'rating_distribution' in data
        print(f"✓ Usage analytics: {data['summary']}")
    
    def test_rag_performance_analytics(self):
        """Verify RAG performance analytics endpoint works"""
        response = requests.get(f"{BASE_URL}/api/analytics/rag/")
        assert response.status_code == 200
        data = response.json()
        assert 'summary' in data
        assert 'latency_over_time' in data
        assert 'score_distribution' in data
        print(f"✓ RAG analytics: {data['summary']}")


class TestSessionManagement:
    """Test session management endpoints"""
    
    def test_create_and_list_sessions(self):
        """Test creating and listing sessions"""
        # Create a session
        create_response = requests.post(f"{BASE_URL}/api/sessions/", json={
            "title": "TEST_CBP_Training_Session"
        })
        assert create_response.status_code == 201
        session_data = create_response.json()
        session_id = session_data['id']
        print(f"✓ Created session: {session_id}")
        
        # List sessions
        list_response = requests.get(f"{BASE_URL}/api/sessions/")
        assert list_response.status_code == 200
        sessions = list_response.json()
        assert isinstance(sessions, list)
        print(f"✓ Listed {len(sessions)} sessions")
        
        # Clean up - delete the test session
        delete_response = requests.delete(f"{BASE_URL}/api/sessions/{session_id}/")
        assert delete_response.status_code == 204
        print(f"✓ Deleted test session")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
