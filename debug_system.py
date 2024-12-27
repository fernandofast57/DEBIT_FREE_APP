
from app import create_app
from config import Config
from app.utils.validation_report import ValidationReport
import asyncio

async def run_system_check():
    app = create_app(Config)
    with app.app_context():
        validator = ValidationReport()
        report = await validator.generate_report()
        
        print("\n=== System Debug Report ===")
        print("\nBlockchain Connection:", "✓" if report['blockchain'].get('connection') else "✗")
        print("Database Status:", "✓" if not report.get('database', {}).get('error') else "✗")
        print("Noble System:", "✓" if report['structure']['noble_system'] else "✗")
        print("\nDetails:", report)

if __name__ == "__main__":
    asyncio.run(run_system_check())
