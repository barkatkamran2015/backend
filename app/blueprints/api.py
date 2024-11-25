from flask import Blueprint, jsonify, request
from ..config import veryfi_config
import requests
from datetime import datetime
import json
from ..categorizer import get_category

api_bp = Blueprint("api", __name__)

@api_bp.route('/process-receipt', methods=['POST'])
def process_receipt():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'File missing from the request'}), 400

        categories = json.loads(request.form.get('categories', '[]'))

        headers = {
            'Accept': 'application/json',
            'Client-Id': veryfi_config['client_id'],
            'Authorization': f"apikey {veryfi_config['username']}:{veryfi_config['api_key']}"
        }
        files = {'file': (file.filename, file, file.content_type)}
        response = requests.post(veryfi_config['api_url'], headers=headers, files=files)
        response.raise_for_status()
        
        vf_data = response.json()

        # Process and validate receipt data...
        receipt_data = process_receipt_data(vf_data, categories)
        return jsonify(receipt_data), 200

    except requests.RequestException as e:
        app.logger.error(f"Request failed: {e}")
        return jsonify({'error': 'Error processing receipt', 'message': str(e)}), 502
    except Exception as e:
        app.logger.error(f"Unhandled exception: {e}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

def process_receipt_data(vf_data, categories):
    date = vf_data.get('date', '')
    vf_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") if date else "N/A"
    vf_items = [item['description'] for item in vf_data.get('line_items', [])]
    vendor = vf_data.get('vendor', {}).get('name', "Unknown Vendor")
    category = get_category(vendor, ", ".join(categories))
    logo_url = get_logo_url(vendor)

    return {
        'id': vf_data.get('id', 'N/A'),
        'vendor': vendor,
        'total': vf_data.get('total', 0.0),
        'category': category,
        'date': vf_date,
        'items': vf_items,
        'logoUrl': logo_url
    }
        return jsonify(receipt_data), 200
    except requests.RequestException as e:
        return jsonify({'error': 'Error processing receipt', 'message': str(e)}), 502
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

def get_logo_url(vendor_name):
    try:
        domain = vendor_name.lower().replace(' ', '') + '.com'
        response = requests.get(f'https://logo.clearbit.com/{domain}')
        if response.status_code == 200:
            return response.url
    except requests.RequestException as e:
        return ''

@api_bp.route("/update-receipt", methods=['PUT'])
def update_receipt():
    try:
        data = request.get_json()
        receipt_id = data.get('id')
        new_category = data.get('category')

        if not receipt_id or not new_category:
            return jsonify({"error": "Invalid data. Receipt ID and category are required."}), 400

        updated_receipt = {
            'id': receipt_id,
            'category': new_category,
            'message': "Category updated successfully"
        }

        return jsonify(updated_receipt), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
