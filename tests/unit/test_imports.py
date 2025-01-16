def test_imports():
    # Test KYC imports
    try:
        from app.models.kyc import KYCDetail, KYCStatus
        print("✓ KYC imports successful")
    except Exception as e:
        print(f"✗ KYC import error: {e}")

    # Test monitoring imports
    try:
        from app.utils.monitoring import monitor_performance
        print("✓ Monitoring imports successful")
    except Exception as e:
        print(f"✗ Monitoring import error: {e}")

    # Test config imports
    try:
        from app.config.constants import TestConfig
        print("✓ Config imports successful")
    except Exception as e:
        print(f"✗ Config import error: {e}")


if __name__ == "__main__":
    test_imports()
