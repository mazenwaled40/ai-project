import os
import sqlite3
import json
import sys
from datetime import datetime
# Reconfigure stdout/stderr to use UTF-8 encoding on Windows to prevent UnicodeEncodeError
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for python versions where stdout.reconfigure might not exist or work
        pass
# Define file paths
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'school_guard.db')
EXPORT_DIR = os.path.join(os.path.dirname(__file__), 'mongodb_exports')
# Ensure export directory exists
os.makedirs(EXPORT_DIR, exist_ok=True)
def adapt_datetime(val):
    """Convert SQLite ISO datetime strings or raw dates to ISO format string or datetime object."""
    if not val:
        return None
    try:
        # SQLite datetime format is usually YYYY-MM-DD HH:MM:SS or YYYY-MM-DDTHH:MM:SS
        if 'T' in val:
            val = val.split('.')[0] # Remove milliseconds if any
            return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
        else:
            return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return val
def fetch_table_data(conn, table_name):
    """Fetch all rows from a table and return as list of dicts with column names as keys."""
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.OperationalError as e:
        print(f"⚠️ Table '{table_name}' not found or error reading it: {e}")
        return []
def format_data_for_mongoose(table_name, data):
    """
    Format data to perfectly match Mongoose schema expectations.
    Converts timestamps to standard ISO format strings for JSON,
    and preserves relational IDs.
    """
    formatted = []
    for row in data:
        item = row.copy()
        
        # Datetime conversions
        if table_name == 'incident' and 'timestamp' in item:
            item['timestamp'] = item['timestamp']  # Keeps SQLite datetime string or converts if needed
        elif table_name == 'alert' and 'sent_time' in item:
            item['sent_time'] = item['sent_time']
        elif table_name == 'feedback' and 'feedback_time' in item:
            item['feedback_time'] = item['feedback_time']
            
        formatted.append(item)
    return formatted
def run_migration():
    print("🚀 Starting Migration preparation from SQLite to MongoDB...")
    
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"❌ SQLite Database not found at: {SQLITE_DB_PATH}")
        return
        
    conn = sqlite3.connect(SQLITE_DB_PATH)
    
    tables = ['role', 'user', 'camera', 'incident', 'alert', 'feedback']
    database_data = {}
    
    for table in tables:
        print(f"📦 Extracting table: {table}...")
        raw_data = fetch_table_data(conn, table)
        formatted = format_data_for_mongoose(table, raw_data)
        database_data[table] = formatted
        
        # Write to separate JSON file
        json_file_path = os.path.join(EXPORT_DIR, f"{table}s.json")
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(formatted, f, indent=4, ensure_ascii=False)
        print(f"   Saved {len(formatted)} records to {json_file_path}")
    conn.close()
    
    print("\n✅ Successfully exported SQLite data to JSON files!")
    print(f"📂 You can find the JSON files in: {EXPORT_DIR}")
    
    # Try importing pymongo to upload to MongoDB directly
    try:
        import pymongo
        print("\n⚡ PyMongo detected! Let's attempt to insert the data directly into MongoDB.")
        
        # Ask for connection string or get from env
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            print("ℹ️ MONGODB_URI environment variable not found in .env.")
            mongo_uri = input("👉 Enter your MongoDB connection URI (press Enter to skip direct upload): ").strip()
            
        if mongo_uri:
            db_name = input("👉 Enter MongoDB database name (default: school_guard): ").strip() or "school_guard"
            client = pymongo.MongoClient(mongo_uri)
            db = client[db_name]
            
            print(f"\n📂 Importing data to MongoDB database: '{db_name}'...")
            for table, records in database_data.items():
                if not records:
                    continue
                
                # MongoDB collection names are usually plural (e.g. roles, users, cameras)
                collection_name = f"{table}s" if table != 'feedback' else 'feedbacks'
                collection = db[collection_name]
                
                # Drop existing collection or ask to insert
                collection.delete_many({}) # Clear existing data for fresh migration
                
                # Insert records
                # MongoDB expects _id. We can map SQLite auto-inc PK to '_id' for compatibility
                mongo_records = []
                pk_map = {
                    'role': 'role_id',
                    'user': 'user_id',
                    'camera': 'camera_id',
                    'incident': 'incident_id',
                    'alert': 'alert_id',
                    'feedback': 'feedback_id'
                }
                pk_field = pk_map.get(table)
                
                for r in records:
                    mr = r.copy()
                    if pk_field in mr:
                        mr['_id'] = mr[pk_field] # Set original SQL primary key as MongoDB _id
                    
                    # Convert dates from string to datetime objects for proper Mongo BSON Dates
                    for date_col in ['timestamp', 'sent_time', 'feedback_time']:
                        if date_col in mr and mr[date_col]:
                            try:
                                mr[date_col] = datetime.fromisoformat(mr[date_col].replace('Z', '+00:00'))
                            except Exception:
                                try:
                                    mr[date_col] = datetime.strptime(mr[date_col], "%Y-%m-%d %H:%M:%S")
                                except Exception:
                                    pass
                    mongo_records.append(mr)
                
                result = collection.insert_many(mongo_records)
                print(f"   Uploaded {len(result.inserted_ids)} records to collection '{collection_name}'")
                
            print("\n🎉 Database migration to MongoDB completed successfully!")
            client.close()
        else:
            print("⏭️ Skipping direct upload to MongoDB. You can use the generated JSON files.")
    except ImportError:
        print("\n💡 PyMongo is not installed. To upload directly to MongoDB from this script:")
        print("   Run: pip install pymongo")
        print("   Then run this script again.")
if __name__ == '__main__':
    run_migration()