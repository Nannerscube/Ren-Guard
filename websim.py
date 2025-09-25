# Fake data Opens flask

from flask import Flask, jsonify
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)
# Enable CORS to allow the HTML file to fetch data from this server
CORS(app)

# A simple dictionary to simulate the recycling data.
# This data is hardcoded and will not change.
mock_material_counts = {
    "Plastic": 12,
    "Cardboard": 8,
    "Glass": 5,
    "Tin": 3
}

# Define the API endpoint that the website will call.
# This function returns the mock data as a JSON response.
@app.route('/data', methods=['GET'])
def get_mock_data():
    """
    Handles GET requests to the /data endpoint.
    Returns a JSON object containing mock recycling counts.
    """
    print("Received request for mock data. Sending response.")
    return jsonify(mock_material_counts)

# Main entry point to run the server.
# It runs on host '0.0.0.0' to be accessible from other devices on the network.
# The port is set to 5000, which matches the HTML file's fetch request.
if __name__ == '__main__':
    print("Starting a simple Flask server for demonstration...")
    app.run(host='0.0.0.0', port=5000)
