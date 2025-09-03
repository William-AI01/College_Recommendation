from database import get_connection
from keys.secret_key import GOOGLE_API_KEY
import google.generativeai as genai

# Configuring the Google API KEY first
genai.configure(api_key=GOOGLE_API_KEY)

def get_embedding(text, model="models/embedding-001"):
    """
    Generate an embedding vector for a given text using GEMINI
    """
    try:
        response = genai.embed_content(model=model, content=text)
        # Doing the embedding in a list, will have to loop through the database later
        return response['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None
    
def college_embedding():
    """
    Fetch college data, make a coherent sentence
    Finally embed that sentence
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, university, location, url FROM colleges;")
    colleges = cur.fetchall()
    cur.close()
    conn.close()

    embedding_colleges = []
    for college in colleges:
        college_id, name, university, location, url = college
        # Creating a sentence that describes the college
        text_to_embed = f"College name: {name}, University: {university}. Location: {location}"

        # Generate the embedding here
        embedding = get_embedding(text_to_embed)

        if embedding:
            embedding_colleges.append({
                "id": college_id,
                "embedding": embedding
            })
    return embedding_colleges

def program_embedding():
    """
    Fetches and embeds the data from programs table
    """
    conn = get_connection()
    cur = conn.cursor()

    # Using a join query here to get the college name 
    cur.execute("""
        SELECT
            p.id,
            p.college_id,
            p.program_name,
            p.duration,
            c.name AS college_name
        FROM
            programs p
        JOIN 
            colleges c ON p.college_id = c.id;
    """)

    programs = cur.fetchall()
    cur.close()
    conn.close()

    program_embedded = []
    for program in programs:
        program_id, college_id, program_name, duration, college_name = program
        
        # Creating a sentence that describes the program
        text_to_embed = f"College: {college_name}. Program Name: {program_name}. Duration: {duration}"

        # Generate the embedding here
        embedding =  get_embedding(text_to_embed)
        if embedding:
            program_embedded.append({
                "id": program_id,
                "college_id": college_id,
                "embedding": embedding
            })
            print(f"Embeded {program_id}")
    return program_embedded

def update_db(data, table_name):
    """
    Adding the embedding for each entries in the Database
    """
    conn = get_connection()
    cur = conn.cursor()

    if table_name == "colleges":
        for item in data:
            cur.execute("""
            UPDATE colleges
            SET embedding = %s
            WHERE id = %s;
            """, (item["embedding"], item["id"])
            )
    elif table_name == "programs":
        for item in data:
            cur.execute("""
            UPDATE programs
            SET embedding = %s
            WHERE id = %s;
            """, (item["embedding"], item["id"])
            )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Successfully updated {len(data)} records in the {table_name} table")

if __name__ == "__main__":
    print("Starting the embedding process and data update...")

    # colleges_with_embedding = college_embedding()
    # update_db(colleges_with_embedding, 'colleges')

    # Embed and update programs 
    programs_with_embedding = program_embedding()
    update_db(programs_with_embedding, 'programs')

    print("Embedding Process Completed Successfully")

