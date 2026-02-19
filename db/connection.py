import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return connection


def test_connection():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions LIMIT 5;")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        return str(e)
