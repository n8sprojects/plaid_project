import os
import json
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask_cors import CORS
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Plaid API
from plaid.api import plaid_api
from plaid.api_client import ApiClient
from plaid.configuration import Configuration

# Models
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_account_filters import LinkTokenAccountFilters
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest


load_dotenv()

app = Flask(__name__)
CORS(app)

USERS_FILE = "users.json"

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV")

configuration = Configuration(
    host=f"https://{PLAID_ENV}.plaid.com",
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)
client = plaid_api.PlaidApi(ApiClient(configuration))


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}  

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    users = load_users()

    if username in users:
        return jsonify({"success": False, "error": "Username already exists"}), 400

    users[username] = {"password": password}  # store hashed password in real app
    save_users(users)
    return jsonify({"success": True, "username": username})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    users = load_users()

    if username not in users or users[username]["password"] != password:
        return jsonify({"success": False, "error": "Invalid username or password"}), 401

    return jsonify({"success": True, "username": username})

@app.route("/create_link_token")
def create_link_token():
    client_user_id = "test_user_1"

    # Create a link token tied to this user
    request_obj = LinkTokenCreateRequest(
        products=[Products("transactions")],  # can also add "auth", "identity", etc.
        client_name="Plaid Test App",
        country_codes=[CountryCode("US")],
        language="en",
        user=LinkTokenCreateRequestUser(
            client_user_id=client_user_id
        )
    )

    # Plaid client setup (replace with your config)
    response = client.link_token_create(request_obj)

    # Return link token to front-end
    return jsonify({"link_token": response.link_token})

@app.route("/exchange_public_token", methods=["POST"])
def exchange_public_token():
    data = request.get_json()
    username = data.get("username")
    public_token = data.get("public_token")
    print(data)

    if not username or not public_token:
        return jsonify({"error": "Missing username or public_token"}), 400

    try:
        request_obj = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(request_obj)
        access_token = exchange_response['access_token']
        print("Access token:", access_token)
    except Exception as e:
        print("Exchange failed:", str(e))
        return jsonify({"error": str(e)}), 400

    # Save token under user's data
    users = load_users()
    if username not in users:
        return jsonify({"error": "User not found"}), 404

    if "banks" not in users[username]:
        users[username]["banks"] = []

    users[username]["banks"].append({
        "access_token": access_token
        # you can store item_id or institution info here too
    })

    save_users(users)
    return jsonify({"message": "Bank connected successfully!"})

if __name__ == "__main__":
    app.run(port=5000)
