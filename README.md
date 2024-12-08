Here's a comprehensive **Markdown** documentation for your **Payment Module** project. This can be saved as `README.md` for your GitHub repository.

---

# Payment Module with Daraja API Integration

This project provides a Python-based **M-Pesa Daraja API Payment Module** for managing vendor subscription payments and handling edge cases like branch limits, payment failures, and subscription downgrades.

---

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Prerequisites](#prerequisites)  
4. [Installation](#installation)  
5. [Configuration](#configuration)  
6. [Usage](#usage)  
7. [Edge Cases Handled](#edge-cases-handled)  
8. [Error Handling](#error-handling)  
9. [Testing Locally](#testing-locally)  
10. [License](#license)

---

## Overview

This module integrates with Safaricom's **Daraja API** to facilitate **Customer-to-Business (C2B)** payments using the **STK Push** method (Lipa na M-Pesa). Vendors can pay for subscriptions based on tiers and add branches with additional fees.

---

## Features

- **Subscription Tiers** with branch limits and pricing.
- **STK Push Payment Integration** using M-Pesa Daraja API.
- **Edge Case Handling**:
  - Branch limits enforcement.
  - Payment failure retries with a grace period.
  - Subscription downgrades with data compliance.
- **Grace Period** for payment retries.
- **Detailed Debugging and Error Handling**.

---

## Prerequisites

Before using this module, ensure you have:

1. **Python 3.x** installed.  
2. **Daraja API Credentials**:
   - **Consumer Key**
   - **Consumer Secret**
   - **Shortcode**
   - **Passkey**
3. **Flask** (for handling callbacks):  
   ```bash
   pip install Flask
   ```
4. **ngrok** (to expose your local server to the internet):  
   [Download ngrok](https://ngrok.com/download)

---

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/payment-module.git
   cd payment-module
   ```

2. **Install Dependencies**:

   ```bash
   pip install requests
   ```

3. **Set Up Flask for Callbacks**:

   Create a `callback_server.py` file with the following content:

   ```python
   from flask import Flask, request, jsonify

   app = Flask(__name__)

   @app.route('/callback', methods=['POST'])
   def callback():
       data = request.get_json()
       print("Callback received:", data)
       return jsonify({"message": "Callback received successfully"}), 200

   if __name__ == '__main__':
       app.run(port=5000, debug=True)
   ```

4. **Run Flask Server**:

   ```bash
   python callback_server.py
   ```

5. **Expose Local Server via ngrok**:

   ```bash
   ngrok http 5000
   ```

   Copy the **ngrok public URL** (e.g., `https://1234abcd.ngrok.io`) for use in the `callback_url`.

---

## Configuration

Create a `config.json` file to store your Daraja API credentials securely:

```json
{
    "consumer_key": "your_consumer_key",
    "consumer_secret": "your_consumer_secret",
    "shortcode": "your_shortcode",
    "passkey": "your_passkey",
    "callback_url": "https://1234abcd.ngrok.io/callback"
}
```

---

## Usage

### 1. Import the `PaymentModule` Class

```python
from payment_module import PaymentModule
```

### 2. Initialize the Payment Module

```python
payment_module = PaymentModule(
    consumer_key="your_consumer_key",
    consumer_secret="your_consumer_secret",
    shortcode="your_shortcode",
    passkey="your_passkey",
    callback_url="https://1234abcd.ngrok.io/callback"
)
```

### 3. Initiate a Payment

```python
phone_number = "254712345678"
subscription_tier = "pro"
num_branches = 5

payment_module.initiate_payment(phone_number, subscription_tier, num_branches)
```

---

## Edge Cases Handled

### 1. Adding Branches Exceeding Limits

- **Starter Tier**: Max 10 branches  
- **Pro Tier**: Max 100 branches  
- **Enterprise Tier**: Unlimited branches

If a vendor attempts to add more than 10 branches at once, an error is returned:

```plaintext
Error: You cannot add more than 10 branches at once.
```

### 2. Payment Failure and Grace Period

If a payment fails due to reasons like insufficient funds, the system starts a **7-day grace period** for the vendor to retry the payment.

```plaintext
Payment failed. A grace period of 7 days has started.
```

### 3. Downgrading Plans

When downgrading to a lower tier, vendors must reduce their branches to comply with the new tier's limits.

---

## Error Handling

The following errors are handled gracefully:

1. **Invalid Phone Numbers**:  
   ```plaintext
   Invalid phone number format. Please use Kenyan international format (e.g., 254712345678).
   ```

2. **Invalid Access Token**:  
   ```plaintext
   Error fetching access token: <error details>
   ```

3. **Payment Processing Errors**:  
   ```plaintext
   Error initiating payment: <error details>
   ```

---

## Testing Locally

1. **Run Flask Server**:  
   ```bash
   python callback_server.py
   ```

2. **Expose via ngrok**:  
   ```bash
   ngrok http 5000
   ```

3. **Set `callback_url`** to the ngrok URL.

4. **Run Payment Module**:  
   ```bash
   python payment_module.py
   ```

5. **Check Logs**:  
   View logs in your terminal or the ngrok web interface (`http://127.0.0.1:4040`).

---

## License

This project is licensed under the **MIT License**.

---

## Contribution

Feel free to fork this repository and contribute by submitting a pull request. For major changes, please open an issue first to discuss what you'd like to change.

---

## Contact

For any inquiries, contact me at:

- **Email**: [your-email@example.com](mailto:your-email@example.com)  
- **GitHub**: [your-username](https://github.com/your-username)

--- 

This documentation covers all the essentials for setting up, configuring, and running the payment module with detailed usage and edge case explanations. 🚀
