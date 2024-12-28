
MOBILE_CONFIG = {
    'api_version': 'v1',
    'min_ios_version': '13.0',
    'min_android_version': '8.0',
    'push_notifications': True,
    'cache_timeout': 300,
    'max_offline_storage': '100MB'
}

def get_mobile_endpoints():
    return {
        'auth': '/api/v1/auth',
        'transactions': '/api/v1/transfers',
        'noble': '/api/v1/noble',
        'admin': '/api/v1/admin/dashboard/mobile'
    }
