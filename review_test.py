#!/usr/bin/env python3
"""
Review-specific test for Django 5 backend APIs for PSPD Guardian chatbot
Tests the exact endpoints and scenarios specified in the review request
"""

import requests
import json
import time
import sys

# Backend URL as specified in review request
BACKEND_URL = "http://localhost:8001"

def test_health_check():
    """Test 1: GET /api/ - Health check"""
    print("🔍 Test 1: Health Check (GET /api/)")
    try:
        response = requests.get(f"{BACKEND_URL}/api/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS: {data}")
            return True
        else:
            print(f"❌ FAIL: Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Exception: {str(e)}")
        return False

def test_service_status():
    """Test 2: GET /api/status/ - Should show all 3 services connected"""
    print("\n🔍 Test 2: Service Status (GET /api/status/)")
    try:
        response = requests.get(f"{BACKEND_URL}/api/status/", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            services = data.get('services', {})
            
            # Check all 3 services are present and connected
            expected_services = ['ollama', 'qdrant', 'postgresql']
            all_connected = all(services.get(service) == True for service in expected_services)
            
            if all_connected:
                print(f"✅ PASS: All 3 services connected - {services}")
                return True
            else:
                print(f"❌ FAIL: Not all services connected - {services}")
                return False
        else:
            print(f"❌ FAIL: Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Exception: {str(e)}")
        return False

def test_chat_initial_message():
    """Test 3: POST /api/chat/ - Send specific message about CrashLoopBackOff"""
    print("\n🔍 Test 3: Chat Initial Message (POST /api/chat/)")
    print("   Sending: 'What is a CrashLoopBackOff error?'")
    print("   ⏳ This may take 30-60 seconds with remote Ollama...")
    
    try:
        payload = {"message": "What is a CrashLoopBackOff error?"}
        start_time = time.time()
        
        # Use 120 second timeout as specified in review
        response = requests.post(f"{BACKEND_URL}/api/chat/", json=payload, timeout=120)
        
        duration = time.time() - start_time
        print(f"   Response received in {duration:.1f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            if all(field in data for field in ['session_id', 'user_message', 'bot_message']):
                bot_message = data['bot_message']
                bot_text = bot_message.get('text', '')
                sources = bot_message.get('sources', [])
                
                if bot_text and len(bot_text) > 0:
                    print(f"✅ PASS: Bot responded with {len(bot_text)} characters")
                    print(f"   Sources from Qdrant: {len(sources)}")
                    print(f"   Bot response preview: {bot_text[:100]}...")
                    
                    # Return session and message info for follow-up tests
                    return {
                        'success': True,
                        'session_id': data['session_id'],
                        'bot_message_id': bot_message.get('id'),
                        'sources_count': len(sources)
                    }
                else:
                    print(f"❌ FAIL: Empty bot response")
                    return {'success': False}
            else:
                print(f"❌ FAIL: Missing required fields in response")
                return {'success': False}
        else:
            print(f"❌ FAIL: Status {response.status_code}: {response.text}")
            return {'success': False}
    except requests.exceptions.Timeout:
        print(f"❌ FAIL: Request timed out after 120 seconds")
        return {'success': False}
    except Exception as e:
        print(f"❌ FAIL: Exception: {str(e)}")
        return {'success': False}

def test_list_sessions():
    """Test 4: GET /api/sessions/ - List sessions"""
    print("\n🔍 Test 4: List Sessions (GET /api/sessions/)")
    try:
        response = requests.get(f"{BACKEND_URL}/api/sessions/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                print(f"✅ PASS: Retrieved {len(data)} sessions")
                return True
            else:
                print(f"❌ FAIL: Response is not a list: {type(data)}")
                return False
        else:
            print(f"❌ FAIL: Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Exception: {str(e)}")
        return False

def test_message_feedback(message_id):
    """Test 5: PATCH /api/messages/<id>/feedback/ - Use bot message ID from test 3"""
    print(f"\n🔍 Test 5: Message Feedback (PATCH /api/messages/{message_id}/feedback/)")
    
    if not message_id:
        print("❌ FAIL: No message ID available from previous test")
        return False
    
    try:
        payload = {"feedback": "up"}
        response = requests.patch(f"{BACKEND_URL}/api/messages/{message_id}/feedback/", 
                                json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('feedback') == 'up':
                print(f"✅ PASS: Feedback updated to 'up'")
                return True
            else:
                print(f"❌ FAIL: Feedback not updated correctly: {data.get('feedback')}")
                return False
        else:
            print(f"❌ FAIL: Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Exception: {str(e)}")
        return False

def test_follow_up_message(session_id):
    """Test 6: POST /api/chat/ - Follow-up message for multi-turn conversation"""
    print(f"\n🔍 Test 6: Follow-up Message (POST /api/chat/)")
    print("   Sending: 'How do I debug it?' to existing session")
    print("   ⏳ This may take 30-60 seconds with remote Ollama...")
    
    if not session_id:
        print("❌ FAIL: No session ID available from previous test")
        return False
    
    try:
        payload = {
            "message": "How do I debug it?",
            "session_id": session_id
        }
        start_time = time.time()
        
        # Use 120 second timeout as specified in review
        response = requests.post(f"{BACKEND_URL}/api/chat/", json=payload, timeout=120)
        
        duration = time.time() - start_time
        print(f"   Response received in {duration:.1f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check that it's using the same session
            if data.get('session_id') == session_id:
                bot_message = data.get('bot_message', {})
                bot_text = bot_message.get('text', '')
                sources = bot_message.get('sources', [])
                
                if bot_text:
                    print(f"✅ PASS: Multi-turn conversation working")
                    print(f"   Session ID: {session_id}")
                    print(f"   Sources from Qdrant: {len(sources)}")
                    print(f"   Bot response preview: {bot_text[:100]}...")
                    return True
                else:
                    print(f"❌ FAIL: Empty bot response in follow-up")
                    return False
            else:
                print(f"❌ FAIL: Session ID mismatch. Expected: {session_id}, Got: {data.get('session_id')}")
                return False
        else:
            print(f"❌ FAIL: Status {response.status_code}: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print(f"❌ FAIL: Request timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"❌ FAIL: Exception: {str(e)}")
        return False

def main():
    """Run the specific review tests"""
    print("🚀 PSPD Guardian Django 5 Backend API Review Tests")
    print("   Backend: http://localhost:8001")
    print("   Remote Ollama: http://31.220.21.156:11434 (llama3.1:8b)")
    print("=" * 70)
    
    results = []
    session_id = None
    message_id = None
    
    # Test 1: Health check
    results.append(test_health_check())
    
    # Test 2: Service status
    results.append(test_service_status())
    
    # Test 3: Initial chat message (stores session_id and message_id)
    chat_result = test_chat_initial_message()
    if chat_result and chat_result.get('success'):
        session_id = chat_result['session_id']
        message_id = chat_result['bot_message_id']
        results.append(True)
    else:
        results.append(False)
    
    # Test 4: List sessions
    results.append(test_list_sessions())
    
    # Test 5: Message feedback (requires message_id from test 3)
    results.append(test_message_feedback(message_id))
    
    # Test 6: Follow-up message (requires session_id from test 3)
    results.append(test_follow_up_message(session_id))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 REVIEW TEST SUMMARY")
    print("=" * 70)
    
    test_names = [
        "Health Check",
        "Service Status", 
        "Chat Initial Message",
        "List Sessions",
        "Message Feedback",
        "Follow-up Message"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All review tests passed!")
        print("\n✅ Django 5 backend with remote Ollama integration is working correctly")
        print("✅ All 3 services (ollama, qdrant, postgresql) are connected")
        print("✅ RAG pipeline with Qdrant vector search is functional")
        print("✅ Multi-turn conversation capability is working")
    else:
        print("⚠️  Some tests failed - check details above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)