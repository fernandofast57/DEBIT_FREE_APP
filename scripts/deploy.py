
import os
import subprocess
import sys

def run_tests():
    """Run pytest suite"""
    print("Running tests...")
    result = subprocess.run(['python', '-m', 'pytest', 'tests/', '--disable-warnings', '-v'])
    return result.returncode == 0

def deploy():
    """Deploy application on Replit"""
    if not run_tests():
        print("Tests failed. Aborting deployment.")
        sys.exit(1)
    
    print("Tests passed. Ready for deployment.")
    print("Use Replit's deployment interface to deploy your changes.")

if __name__ == "__main__":
    deploy()
