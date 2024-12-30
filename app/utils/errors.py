
from typing import Dict, Any
from flask import jsonify

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400, payload: Dict[str, Any] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        rv = dict(self.payload or {})
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

def handle_api_error(error: APIError):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
