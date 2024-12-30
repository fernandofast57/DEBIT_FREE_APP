
import pytest
from app.config.constants import (
    STATUS_VERIFIED,
    STATUS_TO_BE_VERIFIED,
    STATUS_REJECTED,
    STATUS_PENDING
)

def test_status_constants():
    assert STATUS_VERIFIED == 'verified'
    assert STATUS_TO_BE_VERIFIED == 'to_be_verified'
    assert STATUS_REJECTED == 'rejected'
    assert STATUS_PENDING == 'pending'
