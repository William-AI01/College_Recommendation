import json
from typing import List
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import PGVector
from langchain_core.runnables import RunnableLambda
from app.keys.secret_key import GOOGLE_API_KEY
from app.util.database import connection_uri

# Configuring Gemini
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)
# Initialize embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GOOGLE_API_KEY
)



# def load_data(key: str) -> List[Document]:
#     """Load embedded data"""
#     file_paths = {
#         "programs": "./dataset/embedded_programs.json",
#         "colleges": "./dataset/embedded_colleges.json"
#     }
#     file_path = file_paths.get(key)
#     if not file_path:
#         print(f"Invalid key: {key}")
#         return []

#     try:
#         with open(file_path, "r") as f:
#             embedded_data = json.load(f)

#         documents = [
#             Document(
#                 page_content=item["chunk_text"],
#                 metadata={"embedding": item["embedding"]}
#             )
#             for item in embedded_data
#         ]
#         print(f"Done loading {len(documents)} documents from '{file_path}'")
#         return documents
#     except FileNotFoundError:
#         print(f"File not found: {file_path}")
#         return []


# Loading both the JSON files
# programs_doc = load_data("programs_file")
# college_doc = load_data("college_file")

def doc_to_string(docs):
    return "\n\n".join([doc.page_content for doc in docs])

def recommendation_chain():
    """Build and return the LangChain RAG"""
    college_vectorstore = PGVector(
        connection_string=connection_uri,
        embedding_function=embeddings,
        collection_name="college_embed"
    )

    program_vectorstore = PGVector(
        connection_string=connection_uri,
        embedding_function=embeddings,
        collection_name="programs_embed"
    )
    # if not programs_doc or not college_docs:
    #     print("Cannot build RAG chain, missing documents")
    #     return None
    # program_texts = [doc.page_content for doc in programs_doc]
    # program_embeddings = [doc.metadata["embedding"] for doc in programs_doc]

    # college_texts = [doc.page_content for doc in college_docs]
    # college_embeddings = [doc.metadata["embedding"] for doc in college_docs]

    # Create separate in-memory vector stores and retrievers
    # program_vectorstore = DocArrayInMemorySearch.from_documents(programs_doc, embeddings)
    # college_vectorstore = DocArrayInMemorySearch.from_documents(college_docs, embeddings)

    program_retriever = program_vectorstore.as_retriever() | RunnableLambda(doc_to_string)
    college_retriever = college_vectorstore.as_retriever() | RunnableLambda(doc_to_string)

    # Defining the prompt
    prompt_template = ChatPromptTemplate.from_messages([
        ("system",
         "You are a counselor for college and program recommendation."
         " Use the following contexts to provide a detailed and personalized recommendation. \n\n"
         "Your one and only goal is to provide clear, detailed and practical recommendations based on the available information. \n\n"
         "You are given two sources of context: \n"
         "\n\nPROGRAMS:\n{program_context}\n\nCOLLEGES:\n{college_context}"
         "When answering \n"
         "1. Analyze the student's query carefully, and identify what they are looking for "
         "(e.g. field of study, budget, location preferences, and degree type, etc)"
         "2. Cross-reference the relevant PROGRAMS with COLLEGES that offer them. \n"
         "3. Provide 4-5 strong recommendation and just one if they ask for the best with reasons (e.g. reputaion, affortability, quality). \n"
         "4. Suggest next steps such as checking admission criterias, deadlines, scholarships. \n"
         "5. If the Student is unclear, politely ask them to clarify the questions instead of guessing. \n"
         "6. If they ask anything besides colleges and programs, ask them to politely to ask you about your expertise which is colleges and programs in Kathmandu. \n\n"
            "your response should be \n"
            "- Structured, easy to read and student friendly"
            "- Honest: If the data is missing, acknowledge it instead of inventing details"),
        ("human", "Question: {question}")
    ])

    # Build the RAG chain
    rag_chain = (
        RunnableParallel(
            program_context=program_retriever,
            college_context=college_retriever,
            question=RunnablePassthrough()
        )
        | prompt_template
        | model
        | StrOutputParser()
    )
    
    return rag_chain, program_retriever, college_retriever