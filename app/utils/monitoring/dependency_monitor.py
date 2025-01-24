
import pkg_resources
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

def check_outdated_dependencies() -> Dict[str, List[str]]:
    """Check for outdated packages and log warnings"""
    outdated = {}
    
    try:
        for dist in pkg_resources.working_set:
            latest = None
            try:
                latest = pkg_resources.working_set.find(
                    pkg_resources.Requirement.parse(dist.key)
                ).version
                
                if latest != dist.version:
                    if dist.key not in outdated:
                        outdated[dist.key] = []
                    outdated[dist.key].extend([dist.version, latest])
                    logger.warning(f"Package {dist.key} has version {dist.version} but {latest} is available")
            except Exception as e:
                logger.error(f"Error checking version for {dist.key}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error checking dependencies: {str(e)}")
        
    return outdated

def log_dependency_check():
    """Log dependency check results"""
    logger.info(f"Running dependency check at {datetime.now()}")
    outdated = check_outdated_dependencies()
    
    if outdated:
        logger.warning(f"Found {len(outdated)} outdated packages")
        for pkg, versions in outdated.items():
            logger.warning(f"{pkg}: current={versions[0]}, latest={versions[1]}")
    else:
        logger.info("All packages are up to date")
