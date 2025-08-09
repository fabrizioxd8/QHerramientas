#!/usr/bin/env python3
"""
Backend API Testing for Tool Room Inventory Management System
Tests all CRUD operations, checkout/return workflow, and dashboard functionality
"""

import requests
import json
from datetime import datetime, date, timedelta
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"Testing backend at: {API_BASE}")

class ToolRoomTester:
    def __init__(self):
        self.session = requests.Session()
        self.created_tools = []
        self.created_projects = []
        self.created_workers = []
        self.created_checkouts = []
        
    def test_health_check(self):
        """Test if the backend is accessible"""
        print("\n=== Testing Backend Health ===")
        try:
            response = self.session.get(f"{API_BASE}/tools")
            print(f"✅ Backend is accessible - Status: {response.status_code}")
            return True
        except Exception as e:
            print(f"❌ Backend not accessible: {e}")
            return False
    
    def test_tool_management(self):
        """Test Tool CRUD operations"""
        print("\n=== Testing Tool Management API ===")
        
        # Test GET /api/tools (empty initially)
        response = self.session.get(f"{API_BASE}/tools")
        print(f"GET /api/tools - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Retrieved {len(response.json())} existing tools")
        else:
            print(f"❌ Failed to get tools: {response.text}")
            return False
        
        # Test POST /api/tools - Create multiple tools
        test_tools = [
            {
                "name": "Digital Multimeter",
                "description": "Fluke 87V Industrial Multimeter",
                "category": "Electrical",
                "serial_number": "FLK-87V-001",
                "location": "Electrical Lab",
                "calibration_due": (date.today() + timedelta(days=365)).isoformat()
            },
            {
                "name": "Torque Wrench",
                "description": "Precision torque wrench 10-150 Nm",
                "category": "Mechanical",
                "serial_number": "TW-150-002",
                "location": "Tool Crib A"
            },
            {
                "name": "Oscilloscope",
                "description": "Tektronix 4-channel digital oscilloscope",
                "category": "Electrical",
                "serial_number": "TEK-MSO44-003",
                "location": "Electronics Lab"
            }
        ]
        
        for tool_data in test_tools:
            response = self.session.post(f"{API_BASE}/tools", json=tool_data)
            if response.status_code == 200:
                tool = response.json()
                self.created_tools.append(tool)
                print(f"✅ Created tool: {tool['name']} (ID: {tool['id']})")
            else:
                print(f"❌ Failed to create tool {tool_data['name']}: {response.text}")
                return False
        
        # Test GET /api/tools/{id}
        if self.created_tools:
            tool_id = self.created_tools[0]['id']
            response = self.session.get(f"{API_BASE}/tools/{tool_id}")
            if response.status_code == 200:
                tool = response.json()
                print(f"✅ Retrieved tool by ID: {tool['name']}")
            else:
                print(f"❌ Failed to get tool by ID: {response.text}")
                return False
        
        # Test PUT /api/tools/{id}
        if self.created_tools:
            tool_id = self.created_tools[0]['id']
            update_data = {
                "name": "Digital Multimeter - Updated",
                "description": "Fluke 87V Industrial Multimeter - Calibrated",
                "category": "Electrical",
                "serial_number": "FLK-87V-001",
                "location": "Electrical Lab - Bench 1"
            }
            response = self.session.put(f"{API_BASE}/tools/{tool_id}", json=update_data)
            if response.status_code == 200:
                updated_tool = response.json()
                print(f"✅ Updated tool: {updated_tool['name']}")
                self.created_tools[0] = updated_tool
            else:
                print(f"❌ Failed to update tool: {response.text}")
                return False
        
        return True
    
    def test_project_management(self):
        """Test Project CRUD operations"""
        print("\n=== Testing Project Management API ===")
        
        # Test GET /api/projects
        response = self.session.get(f"{API_BASE}/projects")
        print(f"GET /api/projects - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Retrieved {len(response.json())} existing projects")
        else:
            print(f"❌ Failed to get projects: {response.text}")
            return False
        
        # Test POST /api/projects
        test_projects = [
            {
                "name": "Manufacturing Line Upgrade",
                "description": "Upgrade production line with new automation equipment",
                "start_date": date.today().isoformat(),
                "end_date": (date.today() + timedelta(days=90)).isoformat(),
                "required_tools": []
            },
            {
                "name": "Quality Control System",
                "description": "Implement new quality control testing procedures",
                "start_date": (date.today() + timedelta(days=30)).isoformat(),
                "end_date": (date.today() + timedelta(days=120)).isoformat(),
                "required_tools": []
            }
        ]
        
        for project_data in test_projects:
            response = self.session.post(f"{API_BASE}/projects", json=project_data)
            if response.status_code == 200:
                project = response.json()
                self.created_projects.append(project)
                print(f"✅ Created project: {project['name']} (ID: {project['id']})")
            else:
                print(f"❌ Failed to create project {project_data['name']}: {response.text}")
                return False
        
        # Test GET /api/projects/{id}
        if self.created_projects:
            project_id = self.created_projects[0]['id']
            response = self.session.get(f"{API_BASE}/projects/{project_id}")
            if response.status_code == 200:
                project = response.json()
                print(f"✅ Retrieved project by ID: {project['name']}")
            else:
                print(f"❌ Failed to get project by ID: {response.text}")
                return False
        
        # Test PUT /api/projects/{id}
        if self.created_projects:
            project_id = self.created_projects[0]['id']
            update_data = {
                "name": "Manufacturing Line Upgrade - Phase 1",
                "description": "Upgrade production line with new automation equipment - Phase 1 implementation",
                "start_date": date.today().isoformat(),
                "end_date": (date.today() + timedelta(days=60)).isoformat(),
                "required_tools": [self.created_tools[0]['id']] if self.created_tools else []
            }
            response = self.session.put(f"{API_BASE}/projects/{project_id}", json=update_data)
            if response.status_code == 200:
                updated_project = response.json()
                print(f"✅ Updated project: {updated_project['name']}")
                self.created_projects[0] = updated_project
            else:
                print(f"❌ Failed to update project: {response.text}")
                return False
        
        return True
    
    def test_worker_management(self):
        """Test Worker CRUD operations"""
        print("\n=== Testing Worker Management API ===")
        
        # Test GET /api/workers
        response = self.session.get(f"{API_BASE}/workers")
        print(f"GET /api/workers - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Retrieved {len(response.json())} existing workers")
        else:
            print(f"❌ Failed to get workers: {response.text}")
            return False
        
        # Test POST /api/workers
        test_workers = [
            {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@company.com",
                "department": "Manufacturing",
                "phone": "+1-555-0123"
            },
            {
                "name": "Mike Chen",
                "email": "mike.chen@company.com",
                "department": "Quality Control",
                "phone": "+1-555-0124"
            },
            {
                "name": "Emily Rodriguez",
                "email": "emily.rodriguez@company.com",
                "department": "Maintenance",
                "phone": "+1-555-0125"
            }
        ]
        
        for worker_data in test_workers:
            response = self.session.post(f"{API_BASE}/workers", json=worker_data)
            if response.status_code == 200:
                worker = response.json()
                self.created_workers.append(worker)
                print(f"✅ Created worker: {worker['name']} (ID: {worker['id']})")
            else:
                print(f"❌ Failed to create worker {worker_data['name']}: {response.text}")
                return False
        
        # Test GET /api/workers/{id}
        if self.created_workers:
            worker_id = self.created_workers[0]['id']
            response = self.session.get(f"{API_BASE}/workers/{worker_id}")
            if response.status_code == 200:
                worker = response.json()
                print(f"✅ Retrieved worker by ID: {worker['name']}")
            else:
                print(f"❌ Failed to get worker by ID: {response.text}")
                return False
        
        return True
    
    def test_checkout_system(self):
        """Test Tool Checkout System"""
        print("\n=== Testing Tool Checkout System ===")
        
        if not (self.created_tools and self.created_projects and self.created_workers):
            print("❌ Cannot test checkout - missing tools, projects, or workers")
            return False
        
        # Test POST /api/checkout
        checkout_data = {
            "tool_id": self.created_tools[0]['id'],
            "project_id": self.created_projects[0]['id'],
            "worker_id": self.created_workers[0]['id'],
            "expected_return": (date.today() + timedelta(days=7)).isoformat(),
            "notes": "Tool needed for manufacturing line calibration"
        }
        
        response = self.session.post(f"{API_BASE}/checkout", json=checkout_data)
        if response.status_code == 200:
            checkout = response.json()
            self.created_checkouts.append(checkout)
            print(f"✅ Tool checked out successfully (Checkout ID: {checkout['id']})")
            print(f"   Tool: {self.created_tools[0]['name']}")
            print(f"   Project: {self.created_projects[0]['name']}")
            print(f"   Worker: {self.created_workers[0]['name']}")
        else:
            print(f"❌ Failed to checkout tool: {response.text}")
            return False
        
        # Test checkout validation - try to checkout same tool again
        response = self.session.post(f"{API_BASE}/checkout", json=checkout_data)
        if response.status_code == 400:
            print("✅ Checkout validation working - cannot checkout unavailable tool")
        else:
            print(f"❌ Checkout validation failed - should reject unavailable tool")
            return False
        
        # Test checkout with invalid tool ID
        invalid_checkout = checkout_data.copy()
        invalid_checkout['tool_id'] = str(uuid.uuid4())
        response = self.session.post(f"{API_BASE}/checkout", json=invalid_checkout)
        if response.status_code == 404:
            print("✅ Checkout validation working - rejects invalid tool ID")
        else:
            print(f"❌ Checkout validation failed - should reject invalid tool ID")
            return False
        
        return True
    
    def test_return_system(self):
        """Test Tool Return System"""
        print("\n=== Testing Tool Return System ===")
        
        if not self.created_checkouts:
            print("❌ Cannot test return - no active checkouts")
            return False
        
        # Test POST /api/return
        return_data = {
            "checkout_id": self.created_checkouts[0]['id'],
            "notes": "Tool returned in good condition after calibration work"
        }
        
        response = self.session.post(f"{API_BASE}/return", json=return_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Tool returned successfully: {result['message']}")
        else:
            print(f"❌ Failed to return tool: {response.text}")
            return False
        
        # Test return validation - try to return same tool again
        response = self.session.post(f"{API_BASE}/return", json=return_data)
        if response.status_code == 400:
            print("✅ Return validation working - cannot return already returned tool")
        else:
            print(f"❌ Return validation failed - should reject already returned tool")
            return False
        
        # Test return with invalid checkout ID
        invalid_return = {
            "checkout_id": str(uuid.uuid4()),
            "notes": "Invalid test"
        }
        response = self.session.post(f"{API_BASE}/return", json=invalid_return)
        if response.status_code == 404:
            print("✅ Return validation working - rejects invalid checkout ID")
        else:
            print(f"❌ Return validation failed - should reject invalid checkout ID")
            return False
        
        return True
    
    def test_active_checkouts(self):
        """Test Active Checkouts API"""
        print("\n=== Testing Active Checkouts API ===")
        
        # Create another checkout for testing
        if len(self.created_tools) > 1 and self.created_projects and self.created_workers:
            checkout_data = {
                "tool_id": self.created_tools[1]['id'],
                "project_id": self.created_projects[0]['id'],
                "worker_id": self.created_workers[1]['id'] if len(self.created_workers) > 1 else self.created_workers[0]['id'],
                "expected_return": (date.today() + timedelta(days=5)).isoformat(),
                "notes": "Tool needed for quality testing"
            }
            
            response = self.session.post(f"{API_BASE}/checkout", json=checkout_data)
            if response.status_code == 200:
                checkout = response.json()
                self.created_checkouts.append(checkout)
                print(f"✅ Created additional checkout for testing")
        
        # Test GET /api/checkouts/active
        response = self.session.get(f"{API_BASE}/checkouts/active")
        if response.status_code == 200:
            active_checkouts = response.json()
            print(f"✅ Retrieved {len(active_checkouts)} active checkouts")
            
            # Verify structure of active checkouts
            if active_checkouts:
                checkout_item = active_checkouts[0]
                required_keys = ['checkout', 'tool', 'project', 'worker']
                if all(key in checkout_item for key in required_keys):
                    print("✅ Active checkouts have correct structure with related data")
                else:
                    print("❌ Active checkouts missing required related data")
                    return False
        else:
            print(f"❌ Failed to get active checkouts: {response.text}")
            return False
        
        # Test GET /api/checkouts with status filter
        response = self.session.get(f"{API_BASE}/checkouts?status=active")
        if response.status_code == 200:
            checkouts = response.json()
            print(f"✅ Retrieved {len(checkouts)} checkouts with status filter")
        else:
            print(f"❌ Failed to get checkouts with filter: {response.text}")
            return False
        
        return True
    
    def test_dashboard_api(self):
        """Test Dashboard Statistics API"""
        print("\n=== Testing Dashboard Statistics API ===")
        
        # Test GET /api/dashboard
        response = self.session.get(f"{API_BASE}/dashboard")
        if response.status_code == 200:
            dashboard = response.json()
            print("✅ Dashboard API working")
            
            # Verify dashboard structure
            required_fields = [
                'total_tools', 'available_tools', 'checked_out_tools', 
                'maintenance_tools', 'active_projects', 'total_workers', 
                'recent_checkouts'
            ]
            
            missing_fields = [field for field in required_fields if field not in dashboard]
            if missing_fields:
                print(f"❌ Dashboard missing fields: {missing_fields}")
                return False
            
            print(f"   Total Tools: {dashboard['total_tools']}")
            print(f"   Available Tools: {dashboard['available_tools']}")
            print(f"   Checked Out Tools: {dashboard['checked_out_tools']}")
            print(f"   Maintenance Tools: {dashboard['maintenance_tools']}")
            print(f"   Active Projects: {dashboard['active_projects']}")
            print(f"   Total Workers: {dashboard['total_workers']}")
            print(f"   Recent Checkouts: {len(dashboard['recent_checkouts'])}")
            
            # Verify data consistency
            expected_total = len(self.created_tools)
            if dashboard['total_tools'] >= expected_total:
                print("✅ Dashboard tool counts appear consistent")
            else:
                print(f"❌ Dashboard tool count inconsistent - expected at least {expected_total}, got {dashboard['total_tools']}")
                return False
            
        else:
            print(f"❌ Failed to get dashboard: {response.text}")
            return False
        
        return True
    
    def test_error_handling(self):
        """Test API error handling"""
        print("\n=== Testing Error Handling ===")
        
        # Test 404 errors
        fake_id = str(uuid.uuid4())
        
        # Test tool not found
        response = self.session.get(f"{API_BASE}/tools/{fake_id}")
        if response.status_code == 404:
            print("✅ Tool not found error handling works")
        else:
            print(f"❌ Tool not found should return 404, got {response.status_code}")
            return False
        
        # Test project not found
        response = self.session.get(f"{API_BASE}/projects/{fake_id}")
        if response.status_code == 404:
            print("✅ Project not found error handling works")
        else:
            print(f"❌ Project not found should return 404, got {response.status_code}")
            return False
        
        # Test worker not found
        response = self.session.get(f"{API_BASE}/workers/{fake_id}")
        if response.status_code == 404:
            print("✅ Worker not found error handling works")
        else:
            print(f"❌ Worker not found should return 404, got {response.status_code}")
            return False
        
        return True
    
    def cleanup(self):
        """Clean up test data"""
        print("\n=== Cleaning Up Test Data ===")
        
        # Delete created tools
        for tool in self.created_tools:
            try:
                response = self.session.delete(f"{API_BASE}/tools/{tool['id']}")
                if response.status_code == 200:
                    print(f"✅ Deleted tool: {tool['name']}")
                else:
                    print(f"❌ Failed to delete tool {tool['name']}: {response.text}")
            except Exception as e:
                print(f"❌ Error deleting tool {tool['name']}: {e}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Tool Room Inventory Backend Tests")
        print("=" * 60)
        
        test_results = []
        
        # Run tests in order
        tests = [
            ("Backend Health Check", self.test_health_check),
            ("Tool Management API", self.test_tool_management),
            ("Project Management API", self.test_project_management),
            ("Worker Management API", self.test_worker_management),
            ("Tool Checkout System", self.test_checkout_system),
            ("Tool Return System", self.test_return_system),
            ("Active Checkouts API", self.test_active_checkouts),
            ("Dashboard Statistics API", self.test_dashboard_api),
            ("Error Handling", self.test_error_handling)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                test_results.append((test_name, result))
                if not result:
                    print(f"❌ {test_name} FAILED - stopping tests")
                    break
            except Exception as e:
                print(f"❌ {test_name} FAILED with exception: {e}")
                test_results.append((test_name, False))
                break
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\nTotal Tests: {len(test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Backend is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please check the issues above.")
        
        # Cleanup
        self.cleanup()
        
        return failed == 0

if __name__ == "__main__":
    tester = ToolRoomTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)