import os

import psycopg
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

connection = psycopg.connect(
    host=os.environ["PGHOST"],
    port=int(os.environ["PGPORT"]),
    dbname=os.environ["PGDATABASE"],
    user=os.environ["PGUSER"],
    password=os.environ["PGPASSWORD"]
)

print("Connected!")


def create_embedding(text):
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSIONS
        )
    )

    return result.embeddings[0].values


with connection.cursor() as cur:
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS documents (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            content text NOT NULL,
            embedding vector({EMBEDDING_DIMENSIONS}) NOT NULL
        )
    """)

connection.commit()
print("Table ready!")

DOCUMENTS = [
    "PostgreSQL is a relational database.",
    "pgvector adds vector similarity search to PostgreSQL.",
    "Gemini generates embeddings for text.",
    "Python is a programming language.",
]

with connection.cursor() as cur:
    for document in DOCUMENTS:
        cur.execute(
            "INSERT INTO documents (content, embedding) VALUES (%s, %s::vector)",
            (document, str(create_embedding(document)))
        )

connection.commit()
print(f"Inserted {len(DOCUMENTS)} documents!")

query = "How do I store embeddings in a database?"
query_embedding = str(create_embedding(query))

with connection.cursor() as cur:
    cur.execute(
        """
        SELECT content, 1 - (embedding <=> %s::vector) AS similarity
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT 3
        """,
        (query_embedding, query_embedding)
    )
    results = cur.fetchall()

print(f"\nQuery: {query}\n")

for content, similarity in results:
    print(f"{similarity:.3f}  {content}")

connection.close()