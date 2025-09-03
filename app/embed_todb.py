from util.database import get_connection
import json

conn = get_connection()
cur = conn.cursor()

def load_and_insert(json_file, table):
    with open(json_file, "r") as f:
        data = json.load(f)
    
    for item in data:
        chunk_text = item["chunk_text"]
        embeddings = item["embedding"]
        cur.execute(
            f"INSERT INTO {table} (chunk_text, embedding) VALUES (%s, %s)",
            (chunk_text, embeddings)
        )

# Insert the colleges
load_and_insert("./dataset/embedded_colleges.json", "college_embed")

# Insert the programs
load_and_insert("./dataset/embedded_programs.json", "programs_embed")

conn.commit()
cur.close()
conn.close()