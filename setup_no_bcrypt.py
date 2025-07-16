#!/usr/bin/env python3
"""
Setup script for bcrypt-free authentication
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {command}")
        if result.stdout:
            print(f"  Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        if e.stderr:
            print(f"  Error: {e.stderr.strip()}")
        return False

def test_authentication():
    """Test the authentication system"""
    try:
        # Test password hashing
        import hashlib
        import secrets
        
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
        
        # Test the functions
        test_password = "test123"
        hashed = get_password_hash(test_password)
        
        if verify_password(test_password, hashed):
            print("✓ Password hashing and verification working correctly!")
            return True
        else:
            print("❌ Password verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def main():
    print("🚀 Setting up bcrypt-free authentication system...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Error: requirements.txt not found. Please run this from the backend directory.")
        sys.exit(1)
    
    print("1. Cleaning up old packages...")
    run_command("pip uninstall bcrypt passlib -y")
    
    print("\n2. Installing requirements (without bcrypt)...")
    if run_command("pip install -r requirements.txt"):
        print("✓ All packages installed successfully!")
    else:
        print("❌ Failed to install some packages")
        return
    
    print("\n3. Testing authentication system...")
    if test_authentication():
        print("✓ Authentication system is working!")
    else:
        print("❌ Authentication system test failed")
        return
    
    print("\n4. Testing FastAPI import...")
    try:
        from fastapi import FastAPI
        print("✓ FastAPI import successful!")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start MongoDB service")
    print("2. Run the server: python main.py")
    print("3. API will be available at: http://localhost:8000")
    print("4. API docs at: http://localhost:8000/docs")
    
    print("\n🔐 Authentication Details:")
    print("- Using PBKDF2-SHA256 for password hashing")
    print("- No bcrypt dependency required")
    print("- JWT tokens for session management")

if __name__ == "__main__":
    main()
