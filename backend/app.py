import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask_cors import CORS


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

load_dotenv()

app = Flask(__name__)
CORS(app)

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

user_tokens = {}

@app.route("/create_item", methods=["POST"])
def create_item():
    user_id = request.json.get("user_id")
    request_body = SandboxPublicTokenCreateRequest(
        products=[Products.TRANSACTIONS],
        country_codes=[CountryCode('US')],
    )
    public_token_response = client.sandbox_public_token_create(request_body)
    public_token = public_token_response['public_token']

    # Exchange for access token
    exchange_response = client.item_public_token_exchange({'public_token': public_token})
    access_token = exchange_response['access_token']

    # Save token for this user
    user_tokens[user_id] = access_token
    return jsonify({"message": f"Item created for {user_id}", "access_token": access_token})

@app.route("/transactions/<user_id>")
def get_transactions(user_id):
    access_token = user_tokens.get(user_id)
    if not access_token:
        return jsonify({"error": "User not found"}), 404

    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )

    response = client.transactions_get(request)
    return jsonify(response.to_dict())

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

if __name__ == "__main__":
    app.run(port=5000)
