from flask import Blueprint, jsonify, request
from ..config import veryfi_config
import requests
from datetime import datetime
import json
from ..categorizer import get_category

api_bp = Blueprint("api", __name__)

@api_bp.route('/api/process-receipt', methods=['POST'])
def process_receipt():
    # Check if a file is uploaded
    if 'file' not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    try:
        # Prepare data for Veryfi API
        files = {'file': (file.filename, file, file.content_type)}
        headers = {
            'Accept': 'application/json',
            'Client-Id': veryfi_config['client_id'],
            'Authorization': f"apikey {veryfi_config['username']}:{veryfi_config['api_key']}"
        }

        # Send the file to Veryfi
        vf_response = requests.post(veryfi_config['api_url'], headers=headers, files=files)
        vf_response.raise_for_status()
        vf_data = vf_response.json()

        # Extract receipt details
        vendor = vf_data.get('vendor', {}).get('name', "Unknown Vendor")
        total = vf_data.get('total', 0.0)
        date = vf_data.get('date', 'N/A')
        line_items = [item['description'] for item in vf_data.get('line_items', [])]

        # Fetch category
        categories = json.loads(request.form.get('categories', '[]'))
        category = get_category(vendor, ", ".join(categories))

        # Build the response
        receipt_data = {
            'vendor': vendor,
            'total': total,
            'date': date,
            'line_items': line_items,
            'category': category
        }

        return jsonify(receipt_data), 200

    except requests.RequestException as e:
        return jsonify({"message": "Error processing receipt", "error": str(e)}), 502
    except Exception as e:
        return jsonify({"message": "Internal server error", "error": str(e)}), 500
