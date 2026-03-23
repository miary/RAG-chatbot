"""
Test WebSocket streaming feature for RAG chatbot.
Tests: HTTP APIs, WebSocket connection, streaming messages, and fallback behavior.
"""
import pytest
import requests
import json
import os
import time
import websocket

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://chatbot-rag-demo.preview.emergentagent.com').rstrip('/')
WS_URL = BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://')
LOCAL_WS_URL = 'ws://localhost:8001'


class TestHTTPAPIs:
    """Test that existing HTTP APIs still work after WebSocket implementation."""
    
    def test_status_endpoint(self):
        """GET /api/status/ should return service status."""
        response = requests.get(f"{BASE_URL}/api/status/")
        assert response.status_code == 200
        data = response.json()
        assert 'connected' in data
        assert 'services' in data
        assert 'ollama' in data['services']
        assert 'qdrant' in data['services']
        assert 'postgresql' in data['services']
        print(f"Status API: {data}")
    
    def test_chat_endpoint_rest(self):
        """POST /api/chat/ should still work as REST fallback."""
        response = requests.post(
            f"{BASE_URL}/api/chat/",
            json={"message": "Hello, test message"},
            headers={"Content-Type": "application/json"},
            timeout=120  # LLM may have cold-start latency
        )
        assert response.status_code == 200
        data = response.json()
        assert 'session_id' in data
        assert 'user_message' in data
        assert 'bot_message' in data
        assert data['user_message']['text'] == "Hello, test message"
        assert len(data['bot_message']['text']) > 0
        print(f"Chat REST API working, session: {data['session_id']}")
    
    def test_sessions_list(self):
        """GET /api/sessions/ should return list of sessions."""
        response = requests.get(f"{BASE_URL}/api/sessions/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Sessions API: {len(data)} sessions found")
    
    def test_analytics_usage(self):
        """GET /api/analytics/usage/ should return analytics data."""
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        assert response.status_code == 200
        data = response.json()
        assert 'summary' in data
        print(f"Analytics API working")


class TestWebSocketConnection:
    """Test WebSocket endpoint connection and basic functionality."""
    
    def test_websocket_connection_local(self):
        """WebSocket should accept connections at ws://localhost:8001/ws/chat/new/."""
        ws_url = f"{LOCAL_WS_URL}/ws/chat/new/"
        print(f"Testing WebSocket at: {ws_url}")
        
        try:
            ws = websocket.create_connection(ws_url, timeout=10)
            assert ws.connected
            
            # Should receive connection_established message
            result = ws.recv()
            data = json.loads(result)
            assert data['type'] == 'connection_established'
            assert 'session_id' in data
            print(f"WebSocket connected, session: {data['session_id']}")
            
            ws.close()
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {e}")
    
    def test_websocket_ping_pong(self):
        """WebSocket should respond to ping messages."""
        ws_url = f"{LOCAL_WS_URL}/ws/chat/new/"
        
        try:
            ws = websocket.create_connection(ws_url, timeout=10)
            ws.recv()  # Skip connection_established
            
            # Send ping
            ws.send(json.dumps({'type': 'ping'}))
            result = ws.recv()
            data = json.loads(result)
            assert data['type'] == 'pong'
            print("Ping-pong working")
            
            ws.close()
        except Exception as e:
            pytest.fail(f"Ping-pong test failed: {e}")
    
    def test_websocket_invalid_json(self):
        """WebSocket should handle invalid JSON gracefully."""
        ws_url = f"{LOCAL_WS_URL}/ws/chat/new/"
        
        try:
            ws = websocket.create_connection(ws_url, timeout=10)
            ws.recv()  # Skip connection_established
            
            # Send invalid JSON
            ws.send("not valid json")
            result = ws.recv()
            data = json.loads(result)
            assert data['type'] == 'error'
            assert 'Invalid JSON' in data['message']
            print("Invalid JSON handling working")
            
            ws.close()
        except Exception as e:
            pytest.fail(f"Invalid JSON test failed: {e}")
    
    def test_websocket_empty_message(self):
        """WebSocket should reject empty messages."""
        ws_url = f"{LOCAL_WS_URL}/ws/chat/new/"
        
        try:
            ws = websocket.create_connection(ws_url, timeout=10)
            ws.recv()  # Skip connection_established
            
            # Send empty message
            ws.send(json.dumps({'type': 'chat_message', 'message': ''}))
            result = ws.recv()
            data = json.loads(result)
            assert data['type'] == 'error'
            assert 'Empty message' in data['message']
            print("Empty message handling working")
            
            ws.close()
        except Exception as e:
            pytest.fail(f"Empty message test failed: {e}")


class TestWebSocketStreaming:
    """Test WebSocket streaming message flow."""
    
    def test_streaming_message_flow(self):
        """WebSocket should stream response in correct order."""
        ws_url = f"{LOCAL_WS_URL}/ws/chat/new/"
        
        try:
            ws = websocket.create_connection(ws_url, timeout=10)
            
            # Get connection_established
            result = ws.recv()
            data = json.loads(result)
            assert data['type'] == 'connection_established'
            
            # Send chat message
            ws.send(json.dumps({
                'type': 'chat_message',
                'message': 'What is PSPD Guardian?'
            }))
            
            # Collect messages
            messages = []
            message_types = []
            start_time = time.time()
            timeout = 120  # 2 minutes for LLM response
            
            while time.time() - start_time < timeout:
                try:
                    ws.settimeout(5)
                    result = ws.recv()
                    data = json.loads(result)
                    messages.append(data)
                    message_types.append(data['type'])
                    
                    if data['type'] == 'stream_complete':
                        break
                    elif data['type'] == 'error':
                        pytest.fail(f"Received error: {data['message']}")
                except websocket.WebSocketTimeoutException:
                    continue
            
            ws.close()
            
            # Verify message flow
            assert 'user_message_saved' in message_types, "Missing user_message_saved"
            assert 'status' in message_types, "Missing status updates"
            assert 'rag_complete' in message_types, "Missing rag_complete"
            assert 'stream_start' in message_types, "Missing stream_start"
            assert 'stream_chunk' in message_types, "Missing stream_chunk"
            assert 'stream_complete' in message_types, "Missing stream_complete"
            
            # Verify order
            user_saved_idx = message_types.index('user_message_saved')
            rag_complete_idx = message_types.index('rag_complete')
            stream_start_idx = message_types.index('stream_start')
            stream_complete_idx = message_types.index('stream_complete')
            
            assert user_saved_idx < rag_complete_idx, "user_message_saved should come before rag_complete"
            assert rag_complete_idx < stream_start_idx, "rag_complete should come before stream_start"
            assert stream_start_idx < stream_complete_idx, "stream_start should come before stream_complete"
            
            # Verify stream_complete has full response
            stream_complete = next(m for m in messages if m['type'] == 'stream_complete')
            assert 'message' in stream_complete
            assert 'text' in stream_complete['message']
            assert len(stream_complete['message']['text']) > 0
            assert 'sources' in stream_complete['message']
            
            print(f"Streaming flow verified: {len(messages)} messages received")
            print(f"Message types: {message_types[:10]}...")
            
        except Exception as e:
            pytest.fail(f"Streaming test failed: {e}")
    
    def test_streaming_status_updates(self):
        """WebSocket should send status updates (retrieving, generating)."""
        ws_url = f"{LOCAL_WS_URL}/ws/chat/new/"
        
        try:
            ws = websocket.create_connection(ws_url, timeout=10)
            ws.recv()  # Skip connection_established
            
            ws.send(json.dumps({
                'type': 'chat_message',
                'message': 'Test status updates'
            }))
            
            status_messages = []
            start_time = time.time()
            
            while time.time() - start_time < 120:
                try:
                    ws.settimeout(5)
                    result = ws.recv()
                    data = json.loads(result)
                    
                    if data['type'] == 'status':
                        status_messages.append(data)
                    elif data['type'] == 'stream_complete':
                        break
                except websocket.WebSocketTimeoutException:
                    continue
            
            ws.close()
            
            # Verify status updates
            statuses = [m['status'] for m in status_messages]
            assert 'retrieving' in statuses, "Missing 'retrieving' status"
            assert 'generating' in statuses, "Missing 'generating' status"
            
            print(f"Status updates verified: {statuses}")
            
        except Exception as e:
            pytest.fail(f"Status updates test failed: {e}")
    
    def test_streaming_chunks_accumulate(self):
        """Stream chunks should accumulate to form complete response."""
        ws_url = f"{LOCAL_WS_URL}/ws/chat/new/"
        
        try:
            ws = websocket.create_connection(ws_url, timeout=10)
            ws.recv()  # Skip connection_established
            
            ws.send(json.dumps({
                'type': 'chat_message',
                'message': 'Hello'
            }))
            
            chunks = []
            final_text = None
            start_time = time.time()
            
            while time.time() - start_time < 120:
                try:
                    ws.settimeout(5)
                    result = ws.recv()
                    data = json.loads(result)
                    
                    if data['type'] == 'stream_chunk':
                        chunks.append(data['chunk'])
                    elif data['type'] == 'stream_complete':
                        final_text = data['message']['text']
                        break
                except websocket.WebSocketTimeoutException:
                    continue
            
            ws.close()
            
            # Verify chunks accumulate to final text
            accumulated = ''.join(chunks)
            assert accumulated == final_text, f"Chunks don't match final text"
            print(f"Chunks verified: {len(chunks)} chunks = {len(final_text)} chars")
            
        except Exception as e:
            pytest.fail(f"Chunks accumulation test failed: {e}")


class TestDashboard:
    """Test dashboard endpoint still works."""
    
    def test_dashboard_analytics(self):
        """Dashboard analytics endpoints should work."""
        # Usage analytics
        response = requests.get(f"{BASE_URL}/api/analytics/usage/")
        assert response.status_code == 200
        
        # RAG analytics
        response = requests.get(f"{BASE_URL}/api/analytics/rag/")
        assert response.status_code == 200
        
        print("Dashboard analytics endpoints working")


class TestRatingSystem:
    """Test 5-star rating system still works."""
    
    def test_rating_submission(self):
        """Rating submission should work via PATCH."""
        # First create a message via chat
        chat_response = requests.post(
            f"{BASE_URL}/api/chat/",
            json={"message": "Test for rating"},
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        assert chat_response.status_code == 200
        message_id = chat_response.json()['bot_message']['id']
        
        # Submit rating
        rating_response = requests.patch(
            f"{BASE_URL}/api/messages/{message_id}/feedback/",
            json={"rating": 5},
            headers={"Content-Type": "application/json"}
        )
        assert rating_response.status_code == 200
        data = rating_response.json()
        assert data['rating'] == 5
        print(f"Rating system working, rated message {message_id}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
