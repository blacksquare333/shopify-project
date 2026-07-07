from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
CORS(app)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/products")
def products():
    data = supabase.table("shopify").select("*").execute().data
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5001, debug=True)