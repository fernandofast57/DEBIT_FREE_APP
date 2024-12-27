
import os
import subprocess
import sys

def run_format_check():
    """Run black and flake8 for code formatting"""
    print("Running format checks...")
    black_result = subprocess.run(['black', '--check', '.'])
    flake8_result = subprocess.run(['flake8', '.'])
    return black_result.returncode == 0 and flake8_result.returncode == 0

def run_tests():
    """Run pytest suite"""
    print("Running tests...")
    result = subprocess.run(['python', '-m', 'pytest', 'tests/', '--disable-warnings', '-v'])
    return result.returncode == 0

def deploy():
    """Complete deployment process"""
    print("Starting deployment checks...")
    
    # Install test dependencies if not present
    subprocess.run(['pip', 'install', 'black', 'flake8'])
    
    # Run format checks
    if not run_format_check():
        print("❌ Code formatting checks failed. Aborting deployment.")
        sys.exit(1)
    print("✅ Format checks passed.")
    
    # Run tests
    if not run_tests():
        print("❌ Tests failed. Aborting deployment.")
        sys.exit(1)
    print("✅ Tests passed.")
    
    print("✅ All checks passed. Ready for deployment.")
    print("Use Replit's deployment interface to deploy your changes.")

if __name__ == "__main__":
    deploy()
