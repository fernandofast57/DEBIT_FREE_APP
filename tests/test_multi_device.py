
import pytest
from tests.config.test_devices import TEST_DEVICES
from app import create_app

@pytest.mark.parametrize('device_name,device', TEST_DEVICES.items())
def test_responsive_layout(device_name, device):
    app = create_app()
    client = app.test_client()
    
    # Set device-specific headers
    headers = {
        'User-Agent': device.user_agent,
        'Viewport-Width': str(device.screen_size[0])
    }
    
    # Test main endpoints with device configuration
    response = client.get('/', headers=headers)
    assert response.status_code == 200
    
    # Add more device-specific tests here
