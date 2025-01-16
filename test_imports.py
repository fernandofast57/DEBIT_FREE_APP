
from app import create_app
from app.models import User, NobleRank
from app.utils.security import SecurityManager
from app.utils.monitoring import monitor_performance

def test_basic_imports():
    """Test that critical modules can be imported"""
    print("Basic imports successful!")
    app = create_app()
    print("App creation successful!")

if __name__ == "__main__":
    test_basic_imports()
