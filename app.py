import requests
import base64
import os
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv

load_dotenv()

class PaymentModule:
    SUBSCRIPTION_TIERS = {
        "starter": {"price": 100, "limit": 10},      # KES 100, limit of 10 branches/products
        "pro": {"price": 300, "limit": 100},         # KES 300, limit of 100 branches/products
        "enterprise": {"price": 500, "limit": None}  # KES 500, unlimited branches/products
    }

    MAX_BRANCHES_PER_ACTION = 10
    GRACE_PERIOD_DAYS = 7

    def __init__(self, consumer_key, consumer_secret, shortcode, passkey, callback_url):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.shortcode = shortcode
        self.passkey = passkey
        self.callback_url = callback_url
        self.token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        self.stk_push_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        self.failed_payment_attempts = 0
        self.grace_period_end = None

    def get_access_token(self):
        """
        Retrieves an access token from Daraja API.
        """
        try:
            response = requests.get(self.token_url, auth=(self.consumer_key, self.consumer_secret))
            response.raise_for_status()
            access_token_t = response.json()
            access_token = response.json().get('access_token')
            if not access_token:
                print(f"Error: No access token found in the response. Full response: {response.json()}")
            else:
                print(f"Access Token Retrieved: {access_token_t}")
            return access_token
        except requests.RequestException as e:
            print(f"Error fetching access token: {e}")
            return None

    def generate_password(self, timestamp):
        """
        Generates the password required for STK Push.
        """
        data_to_encode = f"{self.shortcode}{self.passkey}{timestamp}"
        encoded_password = base64.b64encode(data_to_encode.encode()).decode('utf-8')
        return encoded_password

    def validate_phone_number(self, phone_number):
        """
        Validates the phone number format (Kenyan international format).
        """
        pattern = re.compile(r"^2547\d{8}$")
        if not pattern.match(phone_number):
            print("Invalid phone number format. Please use Kenyan international format (e.g., 254712345678).")
            return False
        return True

    def validate_branch_limit(self, subscription_tier, num_branches):
        """
        Validates that the number of branches does not exceed limits.
        handles upgrade and downgrades of subscription tiers.
        """
        if num_branches > self.MAX_BRANCHES_PER_ACTION:
            print(f"Error: You cannot add more than {self.MAX_BRANCHES_PER_ACTION} branches at once.")
            return False

        tier_limit = self.SUBSCRIPTION_TIERS[subscription_tier]["limit"]
        if tier_limit is not None and num_branches > tier_limit:
            print(f"Error: The {subscription_tier.capitalize()} plan allows a maximum of {tier_limit} branches.")
            return False

        return True

    def initiate_payment(self, phone_number, subscription_tier, num_branches=0):
        """
        Initiates an STK Push request with edge case handling.
        """
        # Validate phone number
        if not self.validate_phone_number(phone_number):
            return None

        # Validate branch limit
        if not self.validate_branch_limit(subscription_tier, num_branches):
            return None

        # Get the subscription tier details
        tier_details = self.SUBSCRIPTION_TIERS.get(subscription_tier.lower())
        if not tier_details:
            print(f"Invalid subscription tier: {subscription_tier}.")
            return None

        # Calculate total amount
        base_price = tier_details["price"]
        additional_branch_fee = num_branches * 100  # KES 100 per branch
        total_amount = base_price + additional_branch_fee

        account_reference = f"Vendor_{phone_number}"
        transaction_desc = f"{subscription_tier.capitalize()} subscription with {num_branches} branches"

        # Get access token
        access_token = self.get_access_token()
        if not access_token:
            print("Failed to get access token. Payment initiation aborted.")
            return None

        # Generate timestamp and password
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = self.generate_password(timestamp)

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerBuyGoodsOnline",
            "Amount": total_amount,
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }

        try:
            response = requests.post(self.stk_push_url, headers=headers, json=payload)
            response_data = response.json()
            print(f"STK Push Response: {response_data}")

            #  handling payment failure with a retry and grace period
            if response_data.get("ResponseCode") != "0":
                self.handle_payment_failure()
            else:
                print("Payment initiated successfully.")

            return response_data

        except requests.RequestException as e:
            print(f"Error initiating payment: {e}")
            self.handle_payment_failure()
            return None

    def handle_payment_failure(self):
        """
        Handles payment failures by offering retries and a grace period.
        """
        self.failed_payment_attempts += 1
        if self.failed_payment_attempts == 1:
            self.grace_period_end = datetime.now() + timedelta(days=self.GRACE_PERIOD_DAYS)
            print(f"Payment failed. A grace period of {self.GRACE_PERIOD_DAYS} days has started.")

        elif datetime.now() < self.grace_period_end:
            print(f"Payment failed. You have until {self.grace_period_end} to retry the payment.")
        else:
            print("Grace period expired. The business listing is temporarily suspended.")

# Example usage
if __name__ == "__main__":
    # Daraja API credentials and configuration
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    shortcode = "600977"  
    passkey = "passkey"
    callback_url = "http://127.0.0.1:5000/callback"

    # Vendor payment details
    phone_number = "254727200114"
    subscription_tier = "pro"
    num_branches = 5  

    # Create an instance of the payment module
    payment_module = PaymentModule(consumer_key, consumer_secret, shortcode, passkey, callback_url)

    # Initiate the payment
    payment_module.initiate_payment(phone_number, subscription_tier, num_branches)
