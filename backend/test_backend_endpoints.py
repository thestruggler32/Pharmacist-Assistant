"""
Quick test to check if backend endpoints are working
"""
import urllib.request
import json

print("Testing Backend Endpoints...")
print("=" * 60)

# Test 1: Health check
print("\n[1/3] Testing /api/health...")
try:
    with urllib.request.urlopen("http://localhost:5000/api/health") as response:
        data = json.loads(response.read().decode())
        print(f"  ✓ Health check passed: {data}")
except Exception as e:
    print(f"  ✗ Health check failed: {e}")
    print("\n  ⚠️  Backend is not running!")
    print("  Please start the backend with run_dev.bat")
    exit(1)

# Test 2: Login endpoint
print("\n[2/3] Testing /api/auth/login...")
try:
    login_data = {
        "email": "pharmacist@test.com",
        "password": "password"
    }
    
    req = urllib.request.Request(
        "http://localhost:5000/api/auth/login",
        data=json.dumps(login_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print(f"  ✓ Login successful!")
        print(f"    User: {data.get('name')}")
        print(f"    Role: {data.get('role')}")
        
except urllib.error.HTTPError as e:
    error_data = e.read().decode()
    print(f"  ✗ Login failed with HTTP {e.code}")
    print(f"    Error: {error_data}")
except Exception as e:
    print(f"  ✗ Login failed: {e}")

# Test 3: License verification
print("\n[3/3] Testing /api/verify-license...")
try:
    license_data = {
        "license_no": "VALID123",
        "role": "pharmacist"
    }
    
    req = urllib.request.Request(
        "http://localhost:5000/api/verify-license",
        data=json.dumps(license_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print(f"  ✓ License verification: {data}")
        
except urllib.error.HTTPError as e:
    error_data = e.read().decode()
    print(f"  ✗ License verification failed with HTTP {e.code}")
    print(f"    Error: {error_data}")
except Exception as e:
    print(f"  ✗ License verification failed: {e}")

print("\n" + "=" * 60)
print("Backend test complete!")
print("\nIf tests failed:")
print("  1. Make sure backend is running (run_dev.bat)")
print("  2. Check backend console for errors")
print("  3. Backend should show 'Running on http://127.0.0.1:5000'")
