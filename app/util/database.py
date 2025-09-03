import psycopg2

connection_uri = "postgresql://postgres:Something%402025@localhost:5432/College_recommendation"

def get_connection():
    return psycopg2.connect(connection_uri)