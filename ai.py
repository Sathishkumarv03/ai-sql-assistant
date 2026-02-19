import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


# ----------------------------
# SQL GENERATION (LLM)
# ----------------------------
def generate_sql(question):

    prompt = f"""
You are a PostgreSQL expert.

Database schema:
transactions(id, amount, category, transaction_date)

IMPORTANT DATA RULES:
- category values are ONLY: 'Food', 'Rent', 'Transport', 'Shopping'
- transaction_date format is YYYY-MM-DD
- All data is from year 2026
- If user says "expenses", treat it as sum of all categories
- If user mentions month, use EXTRACT(MONTH FROM transaction_date)

Rules:
- Only generate SELECT queries
- Never generate DELETE, UPDATE, INSERT, DROP, ALTER
- Always include LIMIT 100
- Return ONLY raw SQL
- End the query with semicolon
- Do not explain anything

Convert this question into SQL:

Question: {question}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "phi3:mini",
            "prompt": prompt,
            "stream": False
        }
    )

    raw_output = response.json()["response"].strip()

    # --- CLEAN SQL EXTRACTION ---
    select_index = raw_output.upper().find("SELECT")

    if select_index != -1:
        sql_part = raw_output[select_index:]

        # Cut at first semicolon
        semicolon_index = sql_part.find(";")
        if semicolon_index != -1:
            sql_part = sql_part[:semicolon_index]

        sql_part = sql_part.strip()

        # Remove accidental trailing words like 'end'
        sql_part = sql_part.replace(" end", "").replace(" END", "")

        # Ensure LIMIT exists
        if "LIMIT" not in sql_part.upper():
            sql_part += " LIMIT 100"

        sql_part += ";"

        return sql_part

    return raw_output


# ----------------------------
# ANSWER GENERATION (DETERMINISTIC)
# ----------------------------
def generate_answer(question, sql_query, data):

    if not data:
        return "No records found."

    # If SUM query
    if "SUM" in sql_query.upper():
        total = data[0][0]

        if total is None:
            return "No expenses recorded."

        return f"The total amount is ₹{float(total):,.2f}"

    # If returning rows
    lines = []
    for row in data:
        _, amount, category, date = row
        lines.append(f"₹{amount} for {category} on {date}")

    return "\n".join(lines)
