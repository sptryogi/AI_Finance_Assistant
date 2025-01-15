from fastapi import FastAPI, UploadFile, File
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader
import os
from pydantic import BaseModel
from pathlib import Path
from io import BytesIO
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_groq import ChatGroq
from sentence_transformers import CrossEncoder

# Initialize FastAPI app
app = FastAPI()

class QueryRequest(BaseModel):
    query: str

# Database setup
def init_db():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            amount REAL,
            category TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# API Key untuk Groq
os.environ["GROQ_API_KEY"] = "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"

# Initialize LangChain components
db_path = "./data/db"

# Muat semua file markdown di folder parsed_documents
parsed_folder = Path("data/parsed_documents")
documents = []

for markdown_file in parsed_folder.glob("*.md"):  # Pastikan hanya memuat file markdown
    loader = UnstructuredMarkdownLoader(markdown_file)
    documents.extend(loader.load())

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=128)
docs = text_splitter.split_documents(documents)
embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")

qdrant = Qdrant.from_documents(path=db_path, documents=docs, embedding=embeddings, collection_name="financial_embeddings")
retriever = qdrant.as_retriever(search_kwargs={"k": 5})

#Ranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")
#compressor = FlashrankRerank(model=Ranker)
#compressor.model_rebuild()
#compression_retriever = ContextualCompressionRetriever(base_compressor=Ranker, base_retriever=retriever)
llm = ChatGroq(temperature=0, model_name="llama3-70b-8192")

prompt_template = """
    Use the following pieces of information to answer the user's question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    Context: {context}
    Question: {question}

    Answer the question and provide additional helpful information,
    based on the pieces of information, if applicable. Be succinct.

    Responses should be properly formatted to be easily read.
    """

prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt, "verbose": False}
    )

# Function to parse CSV
def parse_csv(file: UploadFile):
    df = pd.read_csv(file.file)
    return df

# Function to parse PDF
def parse_pdf(file: UploadFile):
    reader = PdfReader(file.file)
    text = "\n".join([page.extract_text() for page in reader.pages])
    data = []
    for line in text.splitlines():
        if any(char.isdigit() for char in line):
            data.append(line.split())
    df = pd.DataFrame(data, columns=["Date", "Description", "Amount"])
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    return df

# Function to categorize transactions
def categorize_transactions(df):
    categories = {
        "food": ["restaurant", "groceries", "cafe"],
        "transport": ["taxi", "uber", "fuel"],
        "entertainment": ["movie", "concert", "netflix"],
        "bills": ["electricity", "water", "rent"],
    }
    
    def assign_category(description):
        description = description.lower()
        for category, keywords in categories.items():
            if any(keyword in description for keyword in keywords):
                return category
        return "others"

    df["Category"] = df["Description"].apply(assign_category)
    return df

# Route to upload file
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.filename.endswith(".csv"):
        df = parse_csv(file)
    elif file.filename.endswith(".pdf"):
        df = parse_pdf(file)
    else:
        return {"error": "Unsupported file format"}

    df = categorize_transactions(df)

    # Save to SQLite database
    conn = sqlite3.connect("finance.db")
    df.to_sql("transactions", conn, if_exists="append", index=False)
    conn.close()

    return {"message": "File processed and data saved successfully", "data": df.to_dict(orient="records")}

# Route to generate a report
@app.get("/report")
def generate_report():
    conn = sqlite3.connect("finance.db")
    df = pd.read_sql("SELECT * FROM transactions", conn)
    conn.close()

    if df.empty:
        return {"message": "No data available to generate report"}

    # Group by category
    category_summary = df.groupby("Category")["Amount"].sum()

    # Create a pie chart
    plt.figure(figsize=(8, 8))
    category_summary.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Spending by Category")
    plt.ylabel("")

    # Save the chart to a file
    chart_path = "spending_report.png"
    plt.savefig(chart_path)
    plt.close()

    return {"message": "Report generated successfully", "chart": chart_path}

# Route for answering queries using LangChain
@app.post("/query")
async def query_insights(request: QueryRequest):
    try:
        result = qa_chain.invoke(request.query)
        
        # Ambil hanya jawaban utama dari result
        answer = result.get("result", "No answer available.")
        return {"query": request.query, "response": answer}
    except Exception as e:
        return {"error": str(e), "message": "Failed to process query"}


# Route to generate savings recommendations
@app.get("/recommendations")
def generate_recommendations():
    try:
        conn = sqlite3.connect("finance.db")
        df = pd.read_sql("SELECT * FROM transactions", conn)
        conn.close()

        if df.empty:
            return {"message": "No data available to generate recommendations"}

        # Analyze spending patterns
        category_summary = df.groupby("Category")["Amount"].sum()
        largest_category = category_summary.idxmax()
        largest_amount = category_summary.max()

        recommendations = [
            f"Reduce spending in the '{largest_category}' category, which accounted for the highest expenditure ({largest_amount:.2f}).",
            "Set a monthly budget and track expenses to avoid overspending.",
            "Consider switching to cheaper alternatives for high-cost items."
        ]

        return {"message": "Recommendations generated successfully", "recommendations": recommendations}
    except Exception as e:
        return {"error": str(e), "message": "Failed to generate recommendations"}

# Run the app with Uvicorn (uncomment below for local testing)
if __name__ == "__main__":
     import uvicorn
     uvicorn.run(app, host="0.0.0.0", port=8000)
