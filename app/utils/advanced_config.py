
from app.utils.security.config_manager import AdvancedConfig, DeviceConfig
import logging

def initialize_system(device_id: str = "device-001") -> AdvancedConfig:
    """Initialize the system with advanced configuration"""
    # Initialize configuration
    config = AdvancedConfig()
    
    # Get device configuration
    device_config = config.get_device_config(device_id)
    
    # Check for secret rotation
    config.check_secrets_rotation()
    
    # Log initialization
    config.logger.info("System initialized successfully")
    config.logger.info(f"Device configuration loaded: {device_id}")
    
    return config
