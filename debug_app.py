
import pdb
import sys
from app import create_app
from app.utils.monitoring.performance_monitor import SystemPerformanceMonitor
from app.utils.system_monitor import SystemMonitor
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_application():
    try:
        # Initialize monitors
        perf_monitor = SystemPerformanceMonitor()
        sys_monitor = SystemMonitor()
        
        # Create app in debug mode
        app = create_app()
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        
        # Log startup information
        logger.debug("Starting application in debug mode")
        logger.debug(f"App configuration: {app.config}")
        
        # Interactive debugger point
        pdb.set_trace()
        
        return app
        
    except Exception as e:
        logger.error(f"Debug Error: {str(e)}", exc_info=True)
        pdb.post_mortem()
        return None

if __name__ == "__main__":
    app = debug_application()
    if app:
        # Run app with debug reloader disabled for pdb compatibility
        app.run(host='0.0.0.0', port=3000, debug=True, use_reloader=False)
