import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI
import json
import plotly.express as px
from datetime import datetime, timedelta

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Ginesys AI Assistant", layout="wide")
st.title("🤖 Ginesys AI Data Assistant (Demo Version)")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------
# STEP 1: CREATE SAMPLE DATA
# -----------------------------

@st.cache_data
def generate_sample_data():

    np.random.seed(42)

    stores = ["Mumbai", "Delhi", "Bangalore", "Hyderabad"]
    categories = ["Men", "Women", "Kids", "Accessories"]

    dates = pd.date_range(
        start=datetime.today() - timedelta(days=60),
        end=datetime.today()
    )

    data = []

    for date in dates:
        for store in stores:
            for category in categories:
                sales = np.random.randint(10000, 50000)
                transactions = np.random.randint(50, 200)

                data.append({
                    "date": date,
                    "store": store,
                    "category": category,
                    "sales": sales,
                    "transactions": transactions
                })

    df = pd.DataFrame(data)
    return df


df = generate_sample_data()

# -----------------------------
# STEP 2: INTENT EXTRACTION
# -----------------------------

def extract_intent(user_input):

    prompt = f"""
You are an AI assistant for Ginesys retail ERP.

Convert user request into JSON:

Example:
{{
  "intent": "sales_report / category_analysis / store_comparison",
  "store": "",
  "category": "",
  "date_range_days": number
}}

User: {user_input}

Only return JSON.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

    return response.choices[0].message["content"]

# -----------------------------
# STEP 3: PROCESS DATA
# -----------------------------

def process_query(structured_json):

    query = json.loads(structured_json)

    days = query.get("date_range_days", 7)
    cutoff = datetime.today() - timedelta(days=int(days))

    filtered = df[df["date"] >= cutoff]

    if query["intent"] == "sales_report":

        if query["store"]:
            filtered = filtered[filtered["store"] == query["store"]]

        total_sales = filtered["sales"].sum()

        return filtered, {
            "total_sales": int(total_sales),
            "transactions": int(filtered["transactions"].sum())
        }

    elif query["intent"] == "category_analysis":

        summary = filtered.groupby("category")["sales"].sum().reset_index()
        return summary, summary.to_dict()

    elif query["intent"] == "store_comparison":

        summary = filtered.groupby("store")["sales"].sum().reset_index()
        return summary, summary.to_dict()

    return None, {"message": "Intent not recognized"}

# -----------------------------
# STEP 4: AI INSIGHTS
# -----------------------------

def generate_insights(data_summary):

    prompt = f"""
Analyze this retail data and provide business insights:

{data_summary}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

    return response.choices[0].message["content"]

# -----------------------------
# MAIN CHAT UI
# -----------------------------

user_input = st.text_input("Ask about your business (e.g., Show last 7 days sales for Mumbai)")

if user_input:

    with st.spinner("Analyzing..."):

        structured = extract_intent(user_input)
        st.subheader("🔎 Extracted Intent")
        st.code(structured, language="json")

        data, summary = process_query(structured)

        st.subheader("📊 Data Summary")
        st.write(summary)

        # Charts
        if isinstance(data, pd.DataFrame):
            if "category" in data.columns:
                fig = px.bar(data, x="category", y="sales", title="Category Sales")
                st.plotly_chart(fig)

            elif "store" in data.columns:
                fig = px.bar(data, x="store", y="sales", title="Store Comparison")
                st.plotly_chart(fig)

        insights = generate_insights(summary)

        st.subheader("📈 AI Insights")
        st.write(insights)
