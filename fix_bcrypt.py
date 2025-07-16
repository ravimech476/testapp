#!/usr/bin/env python3
"""
Quick fix script for bcrypt compatibility issues
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🔧 Fixing bcrypt compatibility issues...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Error: requirements.txt not found. Please run this from the backend directory.")
        return
    
    print("1. Uninstalling conflicting packages...")
    run_command("pip uninstall bcrypt passlib -y")
    
    print("\n2. Installing compatible versions...")
    run_command("pip install bcrypt==4.0.1")
    run_command("pip install passlib[bcrypt]==1.7.4")
    
    print("\n3. Installing all requirements...")
    run_command("pip install -r requirements.txt")
    
    print("\n4. Testing bcrypt functionality...")
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        test_hash = pwd_context.hash("test_password")
        if pwd_context.verify("test_password", test_hash):
            print("✓ bcrypt is working correctly!")
        else:
            print("❌ bcrypt verification failed")
    except Exception as e:
        print(f"❌ bcrypt test failed: {e}")
        print("💡 The fallback authentication method will be used")
    
    print("\n" + "=" * 50)
    print("🎉 Fix completed! You can now start the server with:")
    print("   python main.py")

if __name__ == "__main__":
    main()
