from sqlalchemy import inspect,text

def ensure_core_column(engine):
 inspector=inspect(engine)
 if 'specimens' not in inspector.get_table_names():return False
 columns={column['name'] for column in inspector.get_columns('specimens')}
 if 'core' in columns:return False
 with engine.begin() as connection:connection.execute(text("ALTER TABLE specimens ADD COLUMN core VARCHAR(100) NOT NULL DEFAULT ''"))
 return True
