import streamlit as st
import openai
import json
import pandas as pd
import random

# Load OpenAI key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Ginesys AI Assistant", layout="wide")
st.title("🤖 Ginesys AI Data Assistant")

# -----------------------------
# STEP 1: Convert User Prompt to Structured JSON
# -----------------------------

def extract_intent(user_input):
    prompt = f"""
You are an AI assistant for Ginesys ERP system.

Convert the user request into structured JSON format:

Example output:
{{
  "intent": "",
  "store": "",
  "date_range": "",
  "metric": ""
}}

User request: {user_input}

Only return JSON.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message["content"]


# -----------------------------
# STEP 2: Mock Ginesys Data API
# -----------------------------

def fetch_mock_data(structured_json):
    data = json.loads(structured_json)

    # Simulated sales data
    if data["intent"] == "sales_report":
        total_sales = random.randint(100000, 500000)
        previous_sales = random.randint(100000, 500000)

        return {
            "store": data["store"],
            "current_sales": total_sales,
            "previous_sales": previous_sales
        }

    return {"message": "No data found"}


# -----------------------------
# STEP 3: Ask AI to Analyze Data
# -----------------------------

def analyze_data(data):
    prompt = f"""
Analyze this Ginesys data and give business insights:

{data}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message["content"]


# -----------------------------
# MAIN CHAT FLOW
# -----------------------------

user_input = st.text_input("Ask something about your business:")

if user_input:

    with st.spinner("Thinking..."):

        structured = extract_intent(user_input)

        st.subheader("🔎 Extracted Intent")
        st.code(structured, language="json")

        data = fetch_mock_data(structured)

        st.subheader("📊 Data")
        st.write(data)

        insights = analyze_data(data)

        st.subheader("📈 AI Insights")
        st.write(insights)
