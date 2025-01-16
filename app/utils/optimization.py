
from sqlalchemy import text
from app.database import db
import logging

logger = logging.getLogger(__name__)

def optimize_queries():
    """Apply database query optimizations"""
    try:
        with db.engine.connect() as conn:
            # Set pragmas with error handling
            pragmas = [
                "PRAGMA journal_mode=WAL",
                "PRAGMA synchronous=NORMAL", 
                "PRAGMA cache_size=10000",
                "PRAGMA temp_store=MEMORY"
            ]
            
            for pragma in pragmas:
                try:
                    conn.execute(text(pragma))
                    logger.info(f"Successfully executed: {pragma}")
                except Exception as e:
                    logger.error(f"Failed to execute pragma {pragma}: {str(e)}")
                    
        logger.info("Query optimization completed successfully")
    except Exception as e:
        logger.error(f"Error in query optimization: {str(e)}")
        db.session.rollback()

def create_indexes():
    """Create optimized database indexes with improved error handling"""
    try:
        with db.engine.connect() as conn:
            # Tables we expect to work with
            tables = {
                'transactions': [
                    ('idx_transactions_user', 'user_id, created_at'),
                    ('idx_transactions_status', 'status, created_at')
                ],
                'transformations': [
                    ('idx_transformations_date', 'created_at, status'),
                    ('idx_transformations_user', 'user_id, status')
                ],
                'noble_ranks': [
                    ('idx_noble_ranks_level', 'level')
                ],
                'users': [
                    ('idx_users_email', 'email')
                ],
                'noble_relations': [
                    ('idx_noble_relations_user', 'user_id, noble_rank')
                ]
            }
            
            # Check each table and create indexes
            for table_name, indexes in tables.items():
                try:
                    # Check if table exists
                    result = conn.execute(text(
                        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
                    ))
                    
                    if not result.fetchone():
                        logger.warning(f"Table {table_name} does not exist yet, skipping indexes")
                        continue
                        
                    # Get existing indexes
                    existing_indexes = conn.execute(text(
                        f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}'"
                    )).fetchall()
                    existing_index_names = [idx[0] for idx in existing_indexes]
                    
                    # Create or update indexes
                    for index_name, columns in indexes:
                        try:
                            if index_name in existing_index_names:
                                # Drop existing index if it exists
                                conn.execute(text(f"DROP INDEX IF EXISTS {index_name}"))
                                logger.info(f"Dropped existing index {index_name}")
                                
                            # Create new index
                            create_index_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({columns})"
                            conn.execute(text(create_index_sql))
                            logger.info(f"Created index {index_name} on {table_name}")
                            
                        except Exception as e:
                            logger.error(f"Error creating index {index_name} on {table_name}: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error processing table {table_name}: {str(e)}")
                    continue
            
            # Set database optimizations
            optimize_queries()
            
            logger.info("Database optimization completed successfully")
            
    except Exception as e:
        logger.error(f"Error in database optimization: {str(e)}")
        db.session.rollback()
