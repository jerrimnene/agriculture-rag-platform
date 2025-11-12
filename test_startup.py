#!/usr/bin/env python3
"""
Test script to simulate Railway startup and catch errors
"""
import os
import sys
from pathlib import Path

# Set PORT env var like Railway does
os.environ['PORT'] = '8000'

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Testing startup sequence...")
print("=" * 60)

try:
    print("\n1. Testing imports...")
    from src.api.main import app
    print("✓ Imports successful")
    
    print("\n2. Testing app creation...")
    print(f"✓ App created: {app.title}")
    
    print("\n3. Testing health endpoint...")
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Trigger startup event
    with client:
        response = client.get("/health")
        print(f"✓ Health check response: {response.status_code}")
        print(f"  Response body: {response.json()}")
        
        if response.status_code == 200:
            print("\n" + "=" * 60)
            print("✅ SUCCESS! App would start correctly on Railway")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print(f"❌ FAILED! Health check returned {response.status_code}")
            print("=" * 60)
            sys.exit(1)
            
except Exception as e:
    print("\n" + "=" * 60)
    print(f"❌ STARTUP FAILED!")
    print("=" * 60)
    print(f"\nError: {type(e).__name__}: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
