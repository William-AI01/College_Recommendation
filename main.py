from fastapi import FastAPI, HTTPException
from app.schema.schema import RecommendationRequest
from app.recommendation_helper import recommendation_chain, embeddings

app = FastAPI(
    title= "College and Program Recommendation API for Kathmandu",
    description= "A RAG-based API for recommending colleges and programs for students in Kathmandu"
)

# Load documents at startup
# programs_documents = load_data("programs")
# college_documents = load_data("colleges")


# Initialize RAG chain
rag_chain, program_retriever, college_retriever = recommendation_chain()

@app.post("/recommend")
async def get_recommendation(request: RecommendationRequest):
    """
    Endpoint to get college and program recommendations based on user query
    """
    if not rag_chain:
        raise HTTPException(
            status_code=500,
            detail="Recommendation system not initialized properly"
        )
    
    try:
        # Invoke the retrievers and print the results to see the chunks
        # print("\n --- Retrieved Program Chunks: ---")
        # retrieved_programs = program_retriever.invoke(request.query)
        # for doc in retrieved_programs:
        #     print(doc.page_content)

        # print("\n --- Retrieved College Chunks: ---")
        # retrieved_colleges = college_retriever.invoke(request.query)
        # for doc in retrieved_colleges:
        #     print(doc.page_content)
        # Get recommendation from RAG chain
        recommendation = rag_chain.invoke(request.query)
        return {
            "query": request.query,
            "recommendation": recommendation
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing recommendation: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)