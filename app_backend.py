from flask import Flask, render_template, request, jsonify, session, redirect, url_for,send_file
from dataset_generator import generate_dataset
from llm_parser import parse_prompt
from dotenv import load_dotenv
from database import init_db
import numpy as np
import pandas as pd
import sqlite3   
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")  # for sessions
init_db()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()

            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

            conn.commit()
            conn.close()

            return redirect("/login")

        except:
            return render_template("signup.html", error="User already exists")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session["logged_in"] = True
            return redirect("/app")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/app")
def app_page():
    if "logged_in" not in session:
        return redirect("/")
    return render_template("app.html")

@app.route("/generate", methods=["POST"])
def generate():
    if "logged_in" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    user_prompt = data.get("prompt", "")

    try:
        json_output = parse_prompt(user_prompt)
        import json, re
        json_match = re.search(r'\{.*\}', json_output, re.DOTALL)
        config = json.loads(json_match.group())
    except Exception as e:
        return jsonify({"error": "Invalid AI response", "details": str(e)})

    df = generate_dataset(
        rows=config.get("rows", 100),
        columns=config.get("columns", ["id", "name"]),
        missing_rate=config.get("missing_rate", 0),
        add_duplicates=config.get("add_duplicates", False),
        add_outliers=config.get("add_outliers", False),
        add_inconsistent=config.get("add_inconsistent", False),
        add_noise=config.get("add_noise", False),
        imbalance_column=config.get("imbalance_column", None)
    )
    
    all_cols = list(df.columns)

    id_cols = [col for col in all_cols if "id" in col.lower()]

    name_cols = [col for col in all_cols if "name" in col.lower()]

    priority_cols = []
    for col in id_cols + name_cols:
        if col not in priority_cols:
            priority_cols.append(col)

    remaining_cols = [col for col in all_cols if col not in priority_cols]

    df = df[priority_cols + remaining_cols]
    
    df = df.replace({np.nan: None})
    return jsonify(df.to_dict(orient="records"))

from flask import send_file
import pandas as pd

@app.route("/download", methods=["POST"])
def download():
    if "logged_in" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    df = pd.DataFrame(data)

    file_path = "dataset.csv"
    df.to_csv(file_path, index=False)

    return send_file(file_path, as_attachment=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))