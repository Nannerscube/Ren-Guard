# This program runs the web server and stores the data from the detector.

from flask import Flask, jsonify, request
from flask_cors import CORS

# Global variable to store the latest material counts received from the detector
material_counts = {
    "Plastic": 0,
    "Cardboard": 0,
    "Glass": 0,
    "Tin": 0
}

# Flask App setup
app = Flask(__name__)
CORS(app)  # Enable CORS for the web page

# API endpoint to receive data from the separate detector program
@app.route('/post_data', methods=['POST'])
def post_data():
    """
    Receives a JSON payload from the detector and updates the global counts.
    """
    global material_counts
    try:
        data = request.json
        if data:
            material_counts = data
            print(f"Received new data from detector: {material_counts}")
            return jsonify({"status": "success", "message": "Data received"}), 200
        else:
            return jsonify({"status": "error", "message": "No data received"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# API endpoint for the web dashboard to get the latest data
@app.route('/get_data')
def get_data():
    """
    Returns the current material counts as a JSON response for the dashboard.
    """
    print(f"Dashboard requested data. Sending: {material_counts}")
    return jsonify(material_counts)

# Run the Flask app
if __name__ == '__main__':
    # Run on all available network interfaces on port 5000
    app.run(host='0.0.0.0', port=5000)
