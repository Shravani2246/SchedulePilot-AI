import psycopg2

from config import (
    SUPABASE_DB_HOST,
    SUPABASE_DB_NAME,
    SUPABASE_DB_USER,
    SUPABASE_DB_PASSWORD,
    SUPABASE_DB_PORT
)

def get_connection():

    return psycopg2.connect(
        host=SUPABASE_DB_HOST,
        database=SUPABASE_DB_NAME,
        user=SUPABASE_DB_USER,
        password=SUPABASE_DB_PASSWORD,
        port=SUPABASE_DB_PORT
    )