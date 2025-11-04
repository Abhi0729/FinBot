from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from agent import FinBot
from sales_data import get_sales_data, get_data_summary

app = FastAPI(title="FinBot API", version="1.0.0")

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data
sales_df = get_sales_data()
data_summary = get_data_summary(sales_df)

# Initialize FinBot
try:
    finbot = FinBot()
except ValueError as e:
    print(f"Warning: {e}")
    finbot = None

class QuestionRequest(BaseModel):
    question: str

class PredefinedQueryRequest(BaseModel):
    query_type: str

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "FinBot API is running",
        "status": "healthy",
        "llm_available": finbot is not None
    }

@app.get("/sales-data")
def get_sales():
    """Get all sales data"""
    return {
        "data": sales_df.to_dict(orient="records"),
        "summary": data_summary
    }

@app.get("/summary")
def get_summary():
    """Get data summary statistics"""
    return data_summary

@app.post("/ask")
def ask_question(request: QuestionRequest):
    """Ask FinBot a question - interacts directly with LLM"""
    if not finbot:
        raise HTTPException(
            status_code=503, 
            detail="LLM service unavailable. Please set GROQ_API_KEY."
        )
    
    if not request.question or request.question.strip() == "":
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        response = finbot.get_response(request.question, data_summary)
        return {
            "question": request.question,
            "answer": response,
            "source": "llm"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quick-query")
def quick_query(request: PredefinedQueryRequest):
    """Handle predefined queries - interacts directly with LLM for consistent responses"""
    if not finbot:
        raise HTTPException(
            status_code=503,
            detail="LLM service unavailable. Please set GROQ_API_KEY."
        )
    
    query_map = {
        "total_revenue": "What is the total revenue?",
        "top_product": "Which product has the highest revenue?",
        "average_revenue": "What is the average revenue per sale?",
        "sales_by_region": "Show me sales breakdown by region",
        "total_sales": "How many total sales do we have?"
    }
    
    question = query_map.get(request.query_type)
    if not question:
        raise HTTPException(status_code=400, detail="Invalid query type")
    
    try:
        response = finbot.get_response(question, data_summary)
        return {
            "query_type": request.query_type,
            "answer": response,
            "source": "llm_predefined"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prompts")
def get_sample_prompts():
    """Get sample prompts users can try"""
    return {
        "prompts": [
            "What is the total revenue?",
            "Which product generates the most revenue?",
            "Show me sales by region",
            "What's the average revenue per sale?",
            "How is our North region performing?"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)