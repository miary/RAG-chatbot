#!/usr/bin/env python3
"""
Backend API Tests for PSPD Guardian Django Application
Tests all API endpoints according to the review requirements
"""

import requests
import json
import uuid
import sys
from typing import Optional, Dict, Any

# Backend URL from frontend environment
BACKEND_URL = "https://bot-analytics-1.preview.emergentagent.com/api"

class APITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session_id = None
        self.message_id = None
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")
        print()
        
    def test_health_check(self) -> bool:
        """Test GET /api/ - Health check endpoint"""
        print("🔍 Testing Health Check Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_message = "PSPD Guardian API is running"
                expected_status = "ok"
                
                if data.get("message") == expected_message and data.get("status") == expected_status:
                    self.log_test("Health Check", True, f"Response: {data}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_service_status(self) -> bool:
        """Test GET /api/status/ - Service status endpoint"""
        print("🔍 Testing Service Status Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/status/", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has expected structure
                if "connected" in data and "services" in data:
                    services = data.get("services", {})
                    expected_services = ["ollama", "qdrant", "postgresql"]
                    
                    all_services_present = all(service in services for service in expected_services)
                    
                    if all_services_present:
                        self.log_test("Service Status", True, f"Services: {services}")
                        return True
                    else:
                        self.log_test("Service Status", False, f"Missing services in response: {data}")
                        return False
                else:
                    self.log_test("Service Status", False, f"Invalid response structure: {data}")
                    return False
            else:
                self.log_test("Service Status", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Service Status", False, f"Exception: {str(e)}")
            return False
    
    def test_create_session(self) -> bool:
        """Test POST /api/sessions/ - Create new chat session"""
        print("🔍 Testing Create Session Endpoint...")
        try:
            payload = {"title": "Test Chat Session"}
            response = requests.post(f"{self.base_url}/sessions/", json=payload, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                
                # Check if response has expected structure
                if "id" in data and "title" in data and "messages" in data:
                    # Store session_id for later tests
                    self.session_id = data["id"]
                    
                    # Validate UUID format
                    try:
                        uuid.UUID(self.session_id)
                        self.log_test("Create Session", True, f"Session created: {data}")
                        return True
                    except ValueError:
                        self.log_test("Create Session", False, f"Invalid UUID format for session ID: {self.session_id}")
                        return False
                else:
                    self.log_test("Create Session", False, f"Missing fields in response: {data}")
                    return False
            else:
                self.log_test("Create Session", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Session", False, f"Exception: {str(e)}")
            return False
    
    def test_list_sessions(self) -> bool:
        """Test GET /api/sessions/ - List all sessions"""
        print("🔍 Testing List Sessions Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/sessions/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Should be a list
                if isinstance(data, list):
                    # If we created a session, it should be in the list
                    if self.session_id:
                        session_found = any(session.get("id") == self.session_id for session in data)
                        if session_found:
                            self.log_test("List Sessions", True, f"Found {len(data)} sessions including our test session")
                            return True
                        else:
                            self.log_test("List Sessions", False, f"Created session not found in list: {data}")
                            return False
                    else:
                        self.log_test("List Sessions", True, f"Retrieved {len(data)} sessions")
                        return True
                else:
                    self.log_test("List Sessions", False, f"Response is not a list: {data}")
                    return False
            else:
                self.log_test("List Sessions", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("List Sessions", False, f"Exception: {str(e)}")
            return False
    
    def test_get_session_detail(self) -> bool:
        """Test GET /api/sessions/<uuid>/ - Get session detail"""
        print("🔍 Testing Get Session Detail Endpoint...")
        
        if not self.session_id:
            self.log_test("Get Session Detail", False, "No session ID available from previous tests")
            return False
            
        try:
            response = requests.get(f"{self.base_url}/sessions/{self.session_id}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has expected structure
                if "id" in data and "title" in data and "messages" in data:
                    if data["id"] == self.session_id:
                        self.log_test("Get Session Detail", True, f"Session detail: {data}")
                        return True
                    else:
                        self.log_test("Get Session Detail", False, f"Session ID mismatch: expected {self.session_id}, got {data['id']}")
                        return False
                else:
                    self.log_test("Get Session Detail", False, f"Missing fields in response: {data}")
                    return False
            elif response.status_code == 404:
                self.log_test("Get Session Detail", False, "Session not found (404)")
                return False
            else:
                self.log_test("Get Session Detail", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Session Detail", False, f"Exception: {str(e)}")
            return False
    
    def test_send_message_new_session(self) -> bool:
        """Test POST /api/chat/ - Send message (creates new session automatically)"""
        print("🔍 Testing Send Message (New Session) Endpoint...")
        try:
            payload = {"message": "What is error code API-503?"}
            response = requests.post(f"{self.base_url}/chat/", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has expected structure
                required_fields = ["session_id", "user_message", "bot_message"]
                if all(field in data for field in required_fields):
                    # Validate session_id is UUID
                    try:
                        uuid.UUID(data["session_id"])
                    except ValueError:
                        self.log_test("Send Message (New Session)", False, f"Invalid session UUID: {data['session_id']}")
                        return False
                    
                    # Check user message structure
                    user_msg = data["user_message"]
                    if not (user_msg.get("message_type") == "user" and user_msg.get("text")):
                        self.log_test("Send Message (New Session)", False, f"Invalid user message structure: {user_msg}")
                        return False
                    
                    # Check bot message structure
                    bot_msg = data["bot_message"]
                    if not (bot_msg.get("message_type") == "bot" and bot_msg.get("text")):
                        self.log_test("Send Message (New Session)", False, f"Invalid bot message structure: {bot_msg}")
                        return False
                    
                    # Store message ID for feedback test
                    self.message_id = bot_msg.get("id")
                    
                    # Check if bot message has sources (RAG)
                    sources = bot_msg.get("sources", [])
                    
                    self.log_test("Send Message (New Session)", True, 
                                f"Session: {data['session_id']}, Bot response with {len(sources)} sources")
                    return True
                else:
                    self.log_test("Send Message (New Session)", False, f"Missing fields in response: {data}")
                    return False
            else:
                self.log_test("Send Message (New Session)", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Send Message (New Session)", False, f"Exception: {str(e)}")
            return False
    
    def test_send_message_existing_session(self) -> bool:
        """Test POST /api/chat/ - Send message to existing session"""
        print("🔍 Testing Send Message (Existing Session) Endpoint...")
        
        if not self.session_id:
            self.log_test("Send Message (Existing Session)", False, "No session ID available")
            return False
            
        try:
            payload = {
                "message": "Tell me about memory leaks in Guardian systems", 
                "session_id": self.session_id
            }
            response = requests.post(f"{self.base_url}/chat/", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has expected structure
                required_fields = ["session_id", "user_message", "bot_message"]
                if all(field in data for field in required_fields):
                    # Validate session_id matches
                    if data["session_id"] != self.session_id:
                        self.log_test("Send Message (Existing Session)", False, 
                                    f"Session ID mismatch: expected {self.session_id}, got {data['session_id']}")
                        return False
                    
                    bot_msg = data["bot_message"]
                    if bot_msg.get("message_type") == "bot" and bot_msg.get("text"):
                        # Update message ID for feedback test
                        if bot_msg.get("id"):
                            self.message_id = bot_msg["id"]
                            
                        sources = bot_msg.get("sources", [])
                        self.log_test("Send Message (Existing Session)", True, 
                                    f"Response in session {self.session_id} with {len(sources)} sources")
                        return True
                    else:
                        self.log_test("Send Message (Existing Session)", False, f"Invalid bot message: {bot_msg}")
                        return False
                else:
                    self.log_test("Send Message (Existing Session)", False, f"Missing fields: {data}")
                    return False
            elif response.status_code == 404:
                self.log_test("Send Message (Existing Session)", False, "Session not found (404)")
                return False
            else:
                self.log_test("Send Message (Existing Session)", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Send Message (Existing Session)", False, f"Exception: {str(e)}")
            return False
    
    def test_message_feedback(self) -> bool:
        """Test PATCH /api/messages/<uuid>/feedback/ - Update message feedback"""
        print("🔍 Testing Message Feedback Endpoint...")
        
        if not self.message_id:
            self.log_test("Message Feedback", False, "No message ID available from previous tests")
            return False
            
        try:
            payload = {"feedback": "up"}
            response = requests.patch(f"{self.base_url}/messages/{self.message_id}/feedback/", 
                                    json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if feedback was updated
                if data.get("feedback") == "up":
                    self.log_test("Message Feedback", True, f"Feedback updated: {data}")
                    return True
                else:
                    self.log_test("Message Feedback", False, f"Feedback not updated correctly: {data}")
                    return False
            elif response.status_code == 404:
                self.log_test("Message Feedback", False, "Message not found (404)")
                return False
            else:
                self.log_test("Message Feedback", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Message Feedback", False, f"Exception: {str(e)}")
            return False
    
    def test_clear_session(self) -> bool:
        """Test DELETE /api/sessions/<uuid>/clear/ - Clear session messages"""
        print("🔍 Testing Clear Session Messages Endpoint...")
        
        if not self.session_id:
            self.log_test("Clear Session Messages", False, "No session ID available")
            return False
            
        try:
            response = requests.delete(f"{self.base_url}/sessions/{self.session_id}/clear/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "cleared":
                    # Verify messages were cleared by checking session detail
                    detail_response = requests.get(f"{self.base_url}/sessions/{self.session_id}/", timeout=10)
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        messages = detail_data.get("messages", [])
                        
                        if len(messages) == 0:
                            self.log_test("Clear Session Messages", True, "Messages cleared successfully")
                            return True
                        else:
                            self.log_test("Clear Session Messages", False, f"Messages still present: {len(messages)}")
                            return False
                    else:
                        self.log_test("Clear Session Messages", False, "Could not verify clearing via session detail")
                        return False
                else:
                    self.log_test("Clear Session Messages", False, f"Unexpected response: {data}")
                    return False
            elif response.status_code == 404:
                self.log_test("Clear Session Messages", False, "Session not found (404)")
                return False
            else:
                self.log_test("Clear Session Messages", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Clear Session Messages", False, f"Exception: {str(e)}")
            return False
    
    def test_delete_session(self) -> bool:
        """Test DELETE /api/sessions/<uuid>/ - Delete session"""
        print("🔍 Testing Delete Session Endpoint...")
        
        if not self.session_id:
            self.log_test("Delete Session", False, "No session ID available")
            return False
            
        try:
            response = requests.delete(f"{self.base_url}/sessions/{self.session_id}/", timeout=10)
            
            if response.status_code == 204:
                # Verify session was deleted by trying to get it
                detail_response = requests.get(f"{self.base_url}/sessions/{self.session_id}/", timeout=10)
                
                if detail_response.status_code == 404:
                    self.log_test("Delete Session", True, "Session deleted successfully")
                    return True
                else:
                    self.log_test("Delete Session", False, f"Session still exists after deletion: {detail_response.status_code}")
                    return False
            elif response.status_code == 404:
                self.log_test("Delete Session", False, "Session not found (404)")
                return False
            else:
                self.log_test("Delete Session", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete Session", False, f"Exception: {str(e)}")
            return False
    
    def test_ingest_data(self) -> bool:
        """Test POST /api/ingest/ - Ingest mock data"""
        print("🔍 Testing Data Ingestion Endpoint...")
        try:
            response = requests.post(f"{self.base_url}/ingest/", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success" and "documents_ingested" in data:
                    doc_count = data["documents_ingested"]
                    self.log_test("Data Ingestion", True, f"Ingested {doc_count} documents")
                    return True
                else:
                    self.log_test("Data Ingestion", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Data Ingestion", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Data Ingestion", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all API tests and return results"""
        print(f"🚀 Starting PSPD Guardian Backend API Tests")
        print(f"   Backend URL: {self.base_url}")
        print("=" * 60)
        print()
        
        results = {}
        
        # Test sequence based on dependencies
        test_methods = [
            ("Health Check", self.test_health_check),
            ("Service Status", self.test_service_status),
            ("Data Ingestion", self.test_ingest_data),
            ("Create Session", self.test_create_session),
            ("List Sessions", self.test_list_sessions),
            ("Get Session Detail", self.test_get_session_detail),
            ("Send Message (New Session)", self.test_send_message_new_session),
            ("Send Message (Existing Session)", self.test_send_message_existing_session),
            ("Message Feedback", self.test_message_feedback),
            ("Clear Session Messages", self.test_clear_session),
            ("Delete Session", self.test_delete_session),
        ]
        
        for test_name, test_method in test_methods:
            try:
                results[test_name] = test_method()
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
                results[test_name] = False
        
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print()
        print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed - check details above")
        
        return results


def main():
    """Main test execution"""
    tester = APITester()
    results = tester.run_all_tests()
    
    # Exit with error code if any test failed
    if not all(results.values()):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()