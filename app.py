from fastapi import FastAPI
from pydantic import BaseModel
from vanna.remote import VannaDefault
import os
from dotenv import load_dotenv

app = FastAPI()

# Load environment variables
load_dotenv()

# Initialize Vanna
api_key = os.getenv('API')
model = 'quickbooks_2'
vn = VannaDefault(model=model, api_key=api_key)

# Connect to PostgreSQL
vn.connect_to_postgres(
    host=os.getenv('DB_HOST'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT')
)

class Question(BaseModel):
    question: str

@app.post("/ask/")
async def ask_question(question: Question):
    result = vn.ask(question=question.question, visualize=False)
    return str(result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
