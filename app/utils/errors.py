
from flask import jsonify

class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

class BlockchainError(APIError):
    pass

class TransformationError(APIError):
    pass

class BatchProcessingError(APIError):
    pass

class ValidationError(APIError):
    pass
