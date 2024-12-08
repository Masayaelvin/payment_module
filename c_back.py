from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/callback', methods=['POST'])
def callback():
    """
    Endpoint to handle Daraja API callback responses.
    """
    try:
        data = request.get_json()
        print("Callback received:")
        print(jsonify(data))

        # Handle the callback logic here
        result_code = data['Body']['stkCallback']['ResultCode']
        result_desc = data['Body']['stkCallback']['ResultDesc']

        if result_code == 0:
            print("Payment successful!")
            # Extract transaction details
            metadata = data['Body']['stkCallback']['CallbackMetadata']['Item']
            for item in metadata:
                print(f"{item['Name']}: {item['Value']}")
        else:
            print(f"Payment failed: {result_desc}")

        return jsonify({"message": "Callback received successfully"}), 200

    except Exception as e:
        print(f"Error processing callback: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
