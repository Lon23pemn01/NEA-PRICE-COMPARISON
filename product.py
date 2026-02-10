import requests
import sqlite3
import os

def ensure_db(db_path):
    """Create the SQLite database and required table/trigger if missing."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stockx_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            colorway TEXT,
            sku TEXT,
            brand TEXT,
            category TEXT,
            image TEXT,
            slug TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS stockx_products_updated_at
        AFTER UPDATE ON stockx_products
        BEGIN
            UPDATE stockx_products
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END;
    """)
    return conn

def search_stockx(query, db_path="stockx.db"):
    # this will connect to database first to check for a match
    conn = ensure_db(db_path)
    cursor = conn.cursor()
    
    # Split query into words and search for partial matches on each word
    words = query.split()
    
    # Build dynamic query to check for any word match
    conditions = []
    params = []
    for word in words:
        search_pattern = f"%{word}%"
        conditions.append("(name LIKE ? OR sku LIKE ? OR brand LIKE ?)")
        params.extend([search_pattern, search_pattern, search_pattern])
    
    where_clause = " OR ".join(conditions)
    sql = f"""
        SELECT name, colorway, sku, brand, category, image, slug 
        FROM stockx_products 
        WHERE {where_clause}
    """
    
    cursor.execute(sql, params)
    db_results = cursor.fetchall()
    
    if db_results:
        print(f"Found {len(db_results)} matching results in database for '{query}':\n")
        for idx, row in enumerate(db_results, 1):
            name, colorway, sku, brand, category, image, slug = row
            print(f"{idx}. {name} - {colorway}\n   SKU: {sku}, Brand: {brand}, Category: {category}, Image: {image}, Slug: {slug}")
            print(f"   [From database]\n")
        
        conn.close()
        print(f"\nNo API call needed - results served from database.")
        return
    
    print(f"No matches found in database for any word in '{query}'. Fetching from API...\n")
    
    # if there is no database matches, proceed with API call
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "YOUR_API_KEY_HERE"
    }
    
    response = requests.get(
        "https://piloterr.com/api/v2/stockx/search",
        headers=headers,
        params={"query": query}
    )

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Found {len(data)} results from API for '{query}':\n")
            
            added_count = 0
            skipped_count = 0
            
            for idx, item in enumerate(data, 1):
                print(f"{idx}. {item['name']} - {item['colorway']}\n   SKU: {item['sku']}, Brand: {item['brand']}, Category: {item['category']}, Image: {item['image']}, Slug: {item['slug']}")
                
                cursor.execute("SELECT slug FROM stockx_products WHERE slug = ?", (item['slug'],))
                existing = cursor.fetchone()
                
                if existing:
                    print(f"   [Already in database]\n")
                    skipped_count += 1
                else:
                    # add the new product to the database
                    cursor.execute("""
                        INSERT INTO stockx_products (name, colorway, sku, brand, category, image, slug)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (item['name'], item['colorway'], item['sku'], item['brand'], 
                          item['category'], item['image'], item['slug']))
                    print(f"   [Added to database]\n")
                    added_count += 1
            
            conn.commit()
            conn.close()
            
            print(f"\nSummary: {added_count} products added, {skipped_count} already existed in database.")
            
        except Exception as e:
            print(f"Error processing JSON: {e}\nResponse Text: {response.text}")
    else:
        print(f"Error: Status Code {response.status_code}\nResponse: {response.text}")

# Example use
search_stockx("Air Jordan Retro")