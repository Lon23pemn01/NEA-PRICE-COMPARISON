from flask import Flask, render_template, request, redirect, url_for
import requests
import sqlite3
import os

app = Flask(__name__)

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
    """Search for products in database first, then API if needed. Returns list of products and source."""
    # Connect to database and check for existing matches first
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
    print(f"Database search for '{query}' returned {len(db_results)} results.")
    
    if db_results:
        results = []
        for row in db_results:
            name, colorway, sku, brand, category, image, slug = row
            results.append({
                'name': name,
                'colorway': colorway,
                'sku': sku,
                'brand': brand,
                'category': category,
                'image': image,
                'slug': slug,
                'source': 'database'
            })
        conn.close()
        return results, 'database'
    
    # No database matches, proceed with API call
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "39d75a63-1513-4ee1-bb78-6bc20f2b6050"
    }
    
    response = requests.get(
        "https://piloterr.com/api/v2/stockx/search",
        headers=headers,
        params={"query": query}
    )

    if response.status_code == 200:
        try:
            data = response.json()
            results = []
            
            for item in data:
                # Check if slug already exists
                cursor.execute("SELECT slug FROM stockx_products WHERE slug = ?", (item['slug'],))
                existing = cursor.fetchone()
                
                if not existing:
                    # Insert new product
                    cursor.execute("""
                        INSERT INTO stockx_products (name, colorway, sku, brand, category, image, slug)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (item['name'], item['colorway'], item['sku'], item['brand'], 
                          item['category'], item['image'], item['slug']))
                
                results.append({
                    'name': item['name'],
                    'colorway': item['colorway'],
                    'sku': item['sku'],
                    'brand': item['brand'],
                    'category': item['category'],
                    'image': item['image'],
                    'slug': item['slug'],
                    'source': 'api'
                })
            
            conn.commit()
            conn.close()
            return results, 'api'
            
        except Exception as e:
            conn.close()
            print(f"Error processing API response: {str(e)}")
            return [], f'error: {str(e)}'
    else:
        conn.close()
        print(f"API request failed with status {response.status_code}")
        return [], f'error: Status {response.status_code}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product')
def product():
    return render_template('product.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '').strip()
    if not query:
        return redirect(url_for('index'))
    
    results, source = search_stockx(query)
    return render_template('results.html', query=query, results=results, source=source)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('un')
        password = request.form.get('pw')
        confirm_password = request.form.get('cpw')
        if password == confirm_password:
            return redirect(url_for('index'))
        else:
            return render_template('signup.html', error="Passwords do not match")
    return render_template('signup.html')
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)