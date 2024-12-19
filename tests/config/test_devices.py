
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class TestDevice:
    name: str
    user_agent: str
    screen_size: tuple
    capabilities: Dict[str, Any]

TEST_DEVICES = {
    'desktop': TestDevice(
        name='Desktop Chrome',
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
        screen_size=(1920, 1080),
        capabilities={'type': 'desktop', 'touch': False}
    ),
    'mobile': TestDevice(
        name='iPhone 12',
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
        screen_size=(390, 844),
        capabilities={'type': 'mobile', 'touch': True}
    ),
    'tablet': TestDevice(
        name='iPad Air',
        user_agent='Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)',
        screen_size=(820, 1180),
        capabilities={'type': 'tablet', 'touch': True}
    )
}
