#!/usr/bin/env python
import json
import sqlite3
from datetime import datetime

# Pas deze paden aan
JSON_FILE = 'moments_data.json'
DB_FILE = '/home/theo/Documents/travelingguestbook/db.sqlite3'  # Pas dit aan

def load_to_sqlite():
    # Laad JSON data
    with open(JSON_FILE, 'r') as f:
        moments_data = json.load(f)
    
    # Maak database verbinding
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    for data in moments_data:
        try:
            # SQL query om data in te voeren
            query = """
            INSERT INTO streetactivity_moment 
            (id, report, confidence_level, from_practitioner, keywords, 
             date_created, date_modified, activity_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Prepare values
            values = (
                data['id'],
                data['report'],
                data['confidence_level'],
                data['from_practitioner'],
                data.get('keywords', ''),
                data['date_created'],
                data['date_modified'],
                data['activity']
            )
            
            cursor.execute(query, values)
            print(f"✓ Geladen: {data['id']}")
            
        except sqlite3.IntegrityError as e:
            print(f"✗ Duplicaat of constraint error voor {data.get('id', '?')}: {e}")
        except Exception as e:
            print(f"✗ Fout: {e}")
    
    conn.commit()
    conn.close()
    print(f"\n✅ Klaar! {len(moments_data)} momenten geladen.")

if __name__ == '__main__':
    load_to_sqlite()