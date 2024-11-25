from flask import Blueprint, jsonify, request
from ..config import veryfi_config
import requests
from datetime import datetime
import json  # Import json to parse the categories
from ..categorizer import get_category

api_bp = Blueprint("api", __name__)

@api_bp.route("/process-receipt", methods=['POST'])
def process_receipt():
    try:
        # Get the uploaded file from the request
        file = request.files.get('file')
        if not file or not file.filename:
            return jsonify({"error": "No file uploaded or invalid file."}), 400

        # Get categories from the request form data and parse it as a list
        categories = request.form.get('categories', '[]')
        try:
            categories = json.loads(categories)
            if not isinstance(categories, list):
                raise ValueError("Categories must be a list.")
        except (ValueError, json.JSONDecodeError):
            return jsonify({"error": "Invalid categories format. Must be a JSON list."}), 400

        # Set parameters for forwarding image to VeryFI
        files = {
            'file': (file.filename, file, file.content_type)
        }

        # Extract Veryfi API credentials
        vf_client_id = veryfi_config['client_id']
        vf_username = veryfi_config['username']
        vf_api_key = veryfi_config['api_key']
        vf_api_url = veryfi_config['api_url']

        headers = {
            'Accept': 'application/json',
            'Client-Id': vf_client_id,
            'Authorization': f"apikey {vf_username}:{vf_api_key}"
        }

        # Send the file to Veryfi to process
        try:
            vf_response = requests.post(vf_api_url, headers=headers, files=files)
            vf_response.raise_for_status()  # Raise an error for 4xx/5xx responses
            vf_data = vf_response.json()
        except requests.RequestException as e:
            print(f"Error with VeryFI API: {e}")
            return jsonify({"error": "Error processing the receipt. Please try again later."}), 500
        except ValueError as e:
            print(f"Error parsing VeryFI response: {e}")
            return jsonify({"error": "Invalid response from receipt processing service."}), 500

        # Debug: Print full VeryFI response for troubleshooting
        print("VeryFI Response Data:", vf_data)

        # Parse the date
        vf_date = vf_data.get('date', "N/A")
        try:
            vf_date = datetime.strptime(vf_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            vf_date = "N/A"  # Handle invalid or missing dates

        # Extract line items
        vf_items = [item.get('description', 'Unknown Item') for item in vf_data.get('line_items', [])]

        # Extract vendor name and category
        vendor = vf_data.get('vendor', {}).get('name', "Unknown Vendor")
        categories_str = ", ".join(categories)
        category = get_category(vendor, categories_str)

        # Function to fetch logo URL from an external service (e.g., Clearbit Logo API)
        def get_logo_url(vendor_name):
            if not vendor_name or vendor_name == "Unknown Vendor":
                return ''  # Skip logo fetching for unknown vendors
            try:
                domain = vendor_name.lower().replace(' ', '') + '.com'
                response = requests.get(f'https://logo.clearbit.com/{domain}')
                if response.status_code == 200:
                    return f'https://logo.clearbit.com/{domain}'  # Construct and return URL
            except requests.RequestException as e:
                print(f"Error fetching logo for {vendor_name}: {e}")
            return ''  # Return an empty string if the logo is not found or an error occurs

        # Get the logo URL for the vendor
        logo_url = get_logo_url(vendor)

        # Debug: print constructed logo URL
        print("Constructed logo URL:", logo_url)

        # Construct final receipt data
        receipt_data = {
            'id': vf_data.get('id', 'N/A'),  # Ensure an ID is included for frontend use
            'vendor': vendor,
            'total': vf_data.get('total', 0.0),
            'category': category,
            'date': vf_date,
            'items': vf_items,
            'logoUrl': logo_url  # Add the logo URL to the response
        }

        # Debug: print final receipt data
        print("Final Receipt Data:", receipt_data)

        return jsonify(receipt_data), 201

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500


@api_bp.route("/update-receipt", methods=['PUT'])
def update_receipt():
    try:
        # Parse the incoming JSON data
        data = request.get_json()
        receipt_id = data.get('id')
        new_category = data.get('category')

        # Debug: print the incoming data to verify
        print("Received update request for data:", data)

        if not receipt_id or not new_category:
            return jsonify({"error": "Invalid data. Receipt ID and category are required."}), 400

        # Simulate updating receipt category (in a real app, update the database)
        updated_receipt = {
            'id': receipt_id,
            'category': new_category,
            'message': "Category updated successfully"
        }

        # Debug: print updated receipt data
        print("Updated receipt data:", updated_receipt)

        return jsonify(updated_receipt), 200

    except Exception as e:
        print(f"Unexpected error in update-receipt: {e}")
        return jsonify({"error": "An unexpected error occurred while updating the receipt."}), 500
