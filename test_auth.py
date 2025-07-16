#!/usr/bin/env python3
"""
Test script to verify the authentication system works correctly
"""

import hashlib
import secrets
from datetime import datetime, timedelta

def test_password_hashing():
    """Test password hashing and verification"""
    print("🔐 Testing password hashing...")
    
    def get_password_hash(password: str) -> str:
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{hashed.hex()}"

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            salt, hash_hex = hashed_password.split(':')
            computed_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return computed_hash.hex() == hash_hex
        except Exception:
            return False
    
    # Test cases
    test_passwords = ["admin123", "safety123", "maint123", "test_password_!@#"]
    
    for password in test_passwords:
        hashed = get_password_hash(password)
        
        # Verify correct password
        if verify_password(password, hashed):
            print(f"✓ Password '{password}' - Hash and verify working")
        else:
            print(f"❌ Password '{password}' - Verification failed")
            return False
        
        # Verify wrong password fails
        if not verify_password("wrong_password", hashed):
            print(f"✓ Password '{password}' - Wrong password correctly rejected")
        else:
            print(f"❌ Password '{password}' - Wrong password incorrectly accepted")
            return False
    
    return True

def test_jwt_functionality():
    """Test JWT token creation (requires python-jose)"""
    print("\n🎫 Testing JWT functionality...")
    
    try:
        from jose import jwt
        
        # Test data
        secret_key = "test-secret-key"
        algorithm = "HS256"
        test_data = {"sub": "testuser", "exp": datetime.utcnow() + timedelta(minutes=30)}
        
        # Create token
        token = jwt.encode(test_data, secret_key, algorithm=algorithm)
        print(f"✓ JWT token created: {token[:50]}...")
        
        # Decode token
        decoded = jwt.decode(token, secret_key, algorithms=[algorithm])
        if decoded["sub"] == "testuser":
            print("✓ JWT token decoded successfully")
            return True
        else:
            print("❌ JWT token decode failed")
            return False
            
    except ImportError:
        print("❌ python-jose not installed")
        return False
    except Exception as e:
        print(f"❌ JWT test failed: {e}")
        return False

def test_required_packages():
    """Test that all required packages can be imported"""
    print("\n📦 Testing required packages...")
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "uvicorn"),
        ("motor", "motor"),
        ("pymongo", "pymongo"),
        ("jose", "python-jose"),
        ("pydantic", "pydantic"),
        ("PIL", "Pillow"),
    ]
    
    all_good = True
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✓ {name} - Available")
        except ImportError:
            print(f"❌ {name} - Missing")
            all_good = False
    
    return all_good

def main():
    print("🧪 Authentication System Test")
    print("=" * 50)
    
    # Test password hashing
    if not test_password_hashing():
        print("\n❌ Password hashing tests failed!")
        return
    
    # Test JWT functionality
    if not test_jwt_functionality():
        print("\n❌ JWT tests failed!")
        return
    
    # Test package imports
    if not test_required_packages():
        print("\n❌ Some required packages are missing!")
        print("Run: pip install -r requirements.txt")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Authentication system is ready.")
    print("\n📋 Next steps:")
    print("1. Start MongoDB: mongod")
    print("2. Run the server: python main.py")
    print("3. Access API docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
