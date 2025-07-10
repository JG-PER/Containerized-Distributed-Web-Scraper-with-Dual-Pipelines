import os
from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app) # This enables Cross-Origin Resource Sharing

# --- Database connection details ---
DB_HOST = os.getenv('DB_HOST', 'db')
DB_NAME = os.getenv('POSTGRES_DB', 'scraper_data')
DB_USER = os.getenv('POSTGRES_USER', 'user')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')

def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    return conn

@app.route('/api/data')
def get_data():
    """API endpoint to fetch all scraped data."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, content, scraped_at FROM scraped_data ORDER BY scraped_at DESC;")
        data = cur.fetchall()
        cur.close()
        conn.close()
        # Convert list of tuples to list of dictionaries
        results = [{"id": row[0], "content": row[1], "scraped_at": row[2]} for row in data]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)