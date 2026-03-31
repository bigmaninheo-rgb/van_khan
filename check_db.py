#!/usr/bin/env python3
import sqlite3
from pathlib import Path

db_path = Path("c:/Users/Admin/Desktop/app văn khấn/data/vankhan.db")

if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Lấy schema
    cursor.execute("PRAGMA table_info(prayers)")
    columns = cursor.fetchall()
    
    print("Database schema:")
    for col in columns:
        print(f"  {col}")
    
    # Lấy 5 rows đầu tiên
    cursor.execute("SELECT * FROM prayers LIMIT 5")
    rows = cursor.fetchall()
    
    print("\nFirst 5 rows:")
    for row in rows:
        print(f"  {row}")
    
    conn.close()
else:
    print("Database không tồn tại!")
