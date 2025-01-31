
import pytest
from app.models import Transaction, User, TransactionApproval
from app.services.workflow_service import WorkflowService

@pytest.mark.asyncio
async def test_admin_approval_workflow(test_client, test_db):
    """Test complete admin approval workflow"""
    # Setup test data
    admin = User(email="admin@test.com", is_admin=True)
    user = User(email="user@test.com")
    test_db.session.add_all([admin, user])
    await test_db.session.commit()
    
    transaction = Transaction(
        user_id=user.id,
        amount=1000,
        status='pending_approval'
    )
    test_db.session.add(transaction)
    await test_db.session.commit()
    
    # Test approval process
    workflow_service = WorkflowService()
    result = await workflow_service.process_admin_approval(
        transaction_id=transaction.id,
        admin_id=admin.id,
        action='approve'
    )
    
    assert result['status'] == 'approved'
    assert result['processed_by'] == admin.id
    
    # Verify approval record
    approval = TransactionApproval.query.filter_by(
        transaction_id=transaction.id
    ).first()
    assert approval is not None
    assert approval.validator_id == admin.id
