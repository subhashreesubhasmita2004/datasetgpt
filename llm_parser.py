import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

def parse_prompt(user_prompt):

    prompt = f"""
Convert the following dataset request into JSON.

STRICT RULES:
- Only return JSON
- No explanation

Format:
{{
  "rows": number,
  "columns": [],
  "missing_rate": number,
  "add_duplicates": true/false,
  "add_outliers": true/false,
  "add_inconsistent": true/false,
  "add_noise": true/false,
  "imbalance_column": "column_name_or_null"
}}

Examples:

Input: Create dataset with 100 rows, columns age, salary and add missing values
Output:
{{
  "rows": 100,
  "columns": ["age","salary"],
  "missing_rate": 0.1,
  "add_duplicates": false,
  "add_outliers": false,
  "add_inconsistent": false,
  "add_noise": false,
  "imbalance_column": null
}}

Request:
{user_prompt}
"""

    response = model.generate_content(prompt)

    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return text