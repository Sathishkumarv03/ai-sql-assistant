from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from db.connection import get_connection
from ai import generate_sql, generate_answer

app = FastAPI()

# Serve static HTML
app.mount("/static", StaticFiles(directory="static"), name="static")


class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.post("/ask-ai")
def ask_ai(q: Question):

    user_input = q.question.lower()

    # ----------------------------
    # Intent Guard (VERY IMPORTANT)
    # ----------------------------
    allowed_keywords = [
        "transaction", "expense", "amount", "total",
        "food", "rent", "transport", "shopping",
        "january", "february", "march", "april",
        "may", "june", "july", "august",
        "september", "october", "november", "december"
    ]

    if not any(keyword in user_input for keyword in allowed_keywords):
        return {
            "answer": "I can help with financial transaction queries. Please ask about expenses or transactions."
        }

    # ----------------------------
    # Generate SQL
    # ----------------------------
    sql_query = generate_sql(q.question)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.close()

        # ----------------------------
        # Generate Answer
        # ----------------------------
        answer = generate_answer(q.question, sql_query, rows)

        return {
            "answer": answer,
            "generated_sql": sql_query
        }

    except Exception as e:
        return {"error": str(e)}
