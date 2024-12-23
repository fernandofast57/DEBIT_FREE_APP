
import pytest
from app.utils.validation_report import ValidationReport
from app.utils.structure_validator import StructureValidator

@pytest.mark.asyncio
async def test_system_validation():
    validator = ValidationReport()
    report = await validator.generate_report()
    
    # Verify structure validation
    assert 'structure' in report
    structure_results = report['structure']
    
    # Check models naming
    assert structure_results['models']['NobleRelation']['table_name_valid']
    assert structure_results['models']['Transaction']['status_field_valid']
    
    # Check services naming
    assert structure_results['services']['transformation_service']
    assert structure_results['services']['batch_collection_service']
    
    # Check blockchain integration
    assert 'blockchain' in report
    assert report['blockchain']['connection']
    
    # Check batch system
    assert 'batch_system' in report
