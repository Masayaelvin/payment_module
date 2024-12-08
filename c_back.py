from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()
    print("Callback received:", data)
    return jsonify({"message": "Callback received successfully"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
