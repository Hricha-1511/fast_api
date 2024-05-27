from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vanna.remote import VannaDefault
import os
import prompt
from dotenv import load_dotenv
import pandas as pd
import tiktoken
from vanna.openai import OpenAI_Chat
from vanna.vannadb import VannaDB_VectorStore
import os
from typing import Dict, List



app = FastAPI()


# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load environment variables
load_dotenv()
class MyVanna(VannaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        MY_VANNA_MODEL = os.getenv('MODEL')
        MY_VANNA_API_KEY = os.getenv('API')
        VannaDB_VectorStore.__init__(self, vanna_model=MY_VANNA_MODEL, vanna_api_key=MY_VANNA_API_KEY, config=config)
        OpenAI_Chat.__init__(self, config=config)
vn = MyVanna(config={'temperature': 0.7,
                      'max_tokens': 2000,
                     'api_key': os.getenv('OPENAI_API'), 'model': os.getenv('GPT_MODEL')})
# Initialize Vanna
# api_key = os.getenv('API')
# model = os.getenv('MODEL')
# vn = VannaDefault(model=MY_VANNA_MODEL, api_key=api_key)

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
    # result = vn.ask(question=question.question, visualize=False)
    question = question.question
    questions = vn.get_similar_question_sql(question) #get all similar question and query pair
    documentation = vn.get_related_documentation(question) # get all similar documentation
    ddl = vn.get_related_ddl(question) # get all ddl.
    message_log = prompt.get_message_log_prompt(6000, question, ddl, documentation, questions) # create prompt
    
    encoding = tiktoken.encoding_for_model("gpt-4-1106-preview")
    text = str(message_log)
    token_count = len(encoding.encode(text))
    sql_q = vn.submit_prompt(
    [
        vn.system_message(str(message_log) + 'Use sfhmpldata table, only when user query is related to material, items and deliveries or mentioned specifically for the table. \n\nNote: Remove all the extra characters like "\,\n,```sql..```". Strictly provide me the Query part.'),
        vn.user_message(question),
    ]
)
    start_index = sql_q.find("```sql")
    end_index = sql_q.rfind("```")
    # If the substring "```sql" is found
    if start_index != -1:
    # Remove the substring "```sql" from the input string
        sql_q = sql_q[:start_index] + sql_q[start_index + 6:end_index] + sql_q[end_index + 3:]
    else:
    # If the substring "```sql " is not found, output the original string
        sql_q = sql_q
    try:
        result = vn.run_sql(sql_q)
    except Exception as e:
        result = "Incorrect Sql generation"
    
    if isinstance(result, pd.DataFrame):
        result = result.to_json()
        
    # if len(str(result)) > 60000:
    #         result = "Message Too Long to Show"
    return result, sql_q, token_count

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
