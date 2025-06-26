import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del .env

def create_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT"),
            sslmode=os.getenv("DB_SSL_MODE")
        )
        return connection
    except OperationalError as e:
        print(f"❌ Error al conectar a PostgreSQL: {e}")
        return None


def execute_query(query, params=None):
    conn = create_connection()
    if not conn:
        return None
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    result = cursor.fetchall()
                else:
                    result = None
        return result
    except Exception as e:
        print(f"❌ Error ejecutando query: {e}")
        return None
    finally:
        conn.close()