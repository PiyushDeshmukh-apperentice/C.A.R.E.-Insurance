from sqlalchemy import create_engine
import pandas as pd
from config import AUDIT_DATABASE_URL

def view_logs():
    engine = create_engine(AUDIT_DATABASE_URL)
    
    # Pandas makes terminal output pretty
    df = pd.read_sql("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 20", engine)
    
    if df.empty:
        print("📭 Audit log is empty.")
    else:
        # Set display options to ensure columns don't get cut off
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(df)

if __name__ == "__main__":
    view_logs()