from fastapi import FastAPI, Query
from pydantic import BaseModel
import vanna
import json
from vanna.remote import VannaDefault
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
app = FastAPI()

load_dotenv()
# Initialize Vanna
api_key = os.getenv('API')
model = 'quickbooks_2'
vn = VannaDefault(model=model, api_key=api_key)

# Connect to Postgres
vn.connect_to_postgres(host='viaduct.proxy.rlwy.net', dbname='railway', user='readonly_user', password='ratmaxi88888888', port='59459')


class Question(BaseModel):
    question: str


@app.post("/ask/")
async def ask_question(question: str):
    result = vn.ask(question=question, visualize=False)
    # result_json = json.dumps(result)
    # print('************* '+type(result))
    return str(result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=$PORT)
