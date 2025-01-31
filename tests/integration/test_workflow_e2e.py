
import pytest
from app.models import Transaction, User, TransactionApproval
from app.services.workflow_service import WorkflowService
from app.services.notification_service import ServizioNotifiche

@pytest.mark.asyncio
async def test_complete_workflow_e2e(test_client, test_db):
    # Create test user and transaction
    user = User(email="test@example.com", password_hash="test")
    test_db.session.add(user)
    await test_db.session.commit()
    
    transaction = Transaction(
        user_id=user.id,
        amount=1000,
        status='pending'
    )
    test_db.session.add(transaction)
    await test_db.session.commit()
    
    workflow_service = WorkflowService()
    
    # Start workflow
    workflow_data = await workflow_service.start_approval_workflow(transaction.id)
    assert workflow_data['status'] == 'initiated'
    
    # Process each step
    steps = ['document_validation', 'kyc_verification', 'financial_check']
    for step in steps:
        result = await workflow_service.process_step(transaction.id, step, 'approve')
        assert step in [s['step'] for s in result['steps_completed']]
    
    # Verify final status
    final_status = await workflow_service.get_workflow_status(transaction.id)
    assert final_status['current_step'] == 'completed'
    
    # Check notifications
    notification_service = ServizioNotifiche()
    notifications = await notification_service.get_user_notifications(user.id)
    assert len(notifications) > 0

@pytest.mark.asyncio
async def test_rejected_workflow_e2e(test_client, test_db):
    # Similar test for rejection flow
    pass
import pytest
from app.models import Transaction, TransactionApproval
from app.services.workflow_service import WorkflowService

@pytest.mark.asyncio
async def test_complete_workflow_cycle(test_client, test_db, admin_user):
    """Test the complete workflow cycle from creation to approval"""
    # Create test transaction
    transaction = Transaction(
        user_id=1,
        amount=1000,
        type='gold_purchase',
        status='pending_validation'
    )
    test_db.session.add(transaction)
    await test_db.session.commit()
    
    workflow_service = WorkflowService()
    
    # Test document validation
    result = await workflow_service.process_step(
        transaction.id, 
        'document_validation',
        'approve'
    )
    assert result['status'] == 'approved'
    
    # Test KYC verification
    result = await workflow_service.process_step(
        transaction.id,
        'kyc_verification',
        'approve'
    )
    assert result['status'] == 'approved'
    
    # Test final admin approval
    result = await workflow_service.process_admin_approval(
        transaction.id,
        admin_user.id,
        'approve'
    )
    assert result['status'] == 'approve'
    
    # Verify final transaction state
    updated_tx = await Transaction.query.get(transaction.id)
    assert updated_tx.status == 'approved'

@pytest.mark.asyncio
async def test_workflow_rejection_handling(test_client, test_db):
    """Test handling of rejected workflows"""
    transaction = Transaction(
        user_id=1,
        amount=1000,
        type='gold_purchase',
        status='pending_validation'
    )
    test_db.session.add(transaction)
    await test_db.session.commit()
    
    workflow_service = WorkflowService()
    
    result = await workflow_service.process_step(
        transaction.id,
        'document_validation',
        'reject'
    )
    assert result['status'] == 'rejected'
    
    updated_tx = await Transaction.query.get(transaction.id)
    assert updated_tx.status == 'rejected'
