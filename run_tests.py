
import pytest
import sys

def main():
    """Run the test suite with specific options."""
    args = [
        "-v",
        "--disable-warnings",
        "tests/",
        "-p", "no:warnings"
    ]
    return pytest.main(args)

if __name__ == "__main__":
    sys.exit(main())
