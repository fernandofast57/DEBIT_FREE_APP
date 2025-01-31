from app.utils.monitoring.performance_monitor import SystemPerformanceMonitor

def main():
    monitor = SystemPerformanceMonitor()
    monitor.start_monitoring()
    # ... other code using the monitor ...
    monitor.stop_monitoring()

if __name__ == "__main__":
    main()