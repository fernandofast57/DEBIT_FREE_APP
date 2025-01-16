
from sqlalchemy import text
from app.database import db

def optimize_queries():
    """Apply database query optimizations"""
    try:
        with db.engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA cache_size=10000"))
            conn.execute(text("PRAGMA temp_store=MEMORY"))
        db.session.commit()
        print("Query optimization completed successfully")
    except Exception as e:
        print(f"Error optimizing queries: {e}")
        db.session.rollback()

def create_indexes():
    """Create optimized database indexes"""
    try:
        with db.engine.connect() as conn:
            # Check if tables exist
            for table in ['transactions', 'transformations', 'noble_ranks', 'users', 'noble_relations']:
                result = conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                if not result.fetchone():
                    print(f"Table {table} does not exist, skipping indexes")
                    continue
                
                # Drop existing indexes if they exist
                index_check_sql = "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name=?"
                
                # Create indexes based on existing tables
                if table == 'transactions':
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id, created_at)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status, created_at)"))
                elif table == 'transformations':
                    # Check and drop existing index before creating new one
                    existing_indexes = conn.execute(text(index_check_sql), [table]).fetchall()
                    for idx in existing_indexes:
                        if idx[0] in ['idx_transformations_date', 'idx_transformations_user']:
                            conn.execute(text(f"DROP INDEX IF EXISTS {idx[0]}"))
                    
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_transformations_date ON transformations(created_at, status)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_transformations_user ON transformations(user_id, status)"))
                elif table == 'noble_ranks':
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_noble_ranks_level ON noble_ranks(level)"))
                elif table == 'users':
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"))
                elif table == 'noble_relations':
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_noble_relations_user ON noble_relations(user_id, noble_rank)"))

            # Optimize SQLite
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA cache_size=10000"))
            conn.execute(text("PRAGMA temp_store=MEMORY"))
            
        db.session.commit()
        print("Database optimization completed successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")
        db.session.rollback()
