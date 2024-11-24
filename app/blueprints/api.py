from flask import Blueprint, jsonify, request
import os
import requests
from datetime import datetime
import json
from ..categorizer import get_category

api_bp = Blueprint("api", __name__)

# Load Veryfi API credentials from environment variables
VERYFI_CLIENT_ID = os.getenv("VERYFI_CLIENT_ID")
VERYFI_CLIENT_SECRET = os.getenv("VERYFI_CLIENT_SECRET")
VERYFI_USERNAME = os.getenv("VERYFI_USERNAME")
VERYFI_API_KEY = os.getenv("VERYFI_API_KEY")
VERYFI_API_URL = os.getenv("VERYFI_API_URL", "https://api.veryfi.com/api/v7/partner/documents/")

@api_bp.route("/process-receipt", methods=["POST"])
def process_receipt():
    # Get the uploaded file from the request
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Parse categories from the request, if available
    try:
        categories = json.loads(request.form.get("categories", "[]"))
    except json.JSONDecodeError:
        categories = []

    # Set up the headers for Veryfi API
    headers = {
        "Accept": "application/json",
        "Client-Id": VERYFI_CLIENT_ID,
        "Authorization": f"apikey {VERYFI_USERNAME}:{VERYFI_API_KEY}"
    }

    # Forward the file to Veryfi for processing
    try:
        files = {"file": (file.filename, file, file.content_type)}
        response = requests.post(VERYFI_API_URL, headers=headers, files=files)
        response.raise_for_status()  # Raise exception for HTTP errors
        vf_data = response.json()
    except requests.RequestException as e:
        print(f"Error calling Veryfi API: {e}")
        return jsonify({"error": "Failed to process receipt with Veryfi."}), 500

    # Debug: log the full Veryfi response
    print("Veryfi Response:", vf_data)

    # Handle the date field
    vf_date = vf_data.get("date", "N/A")
    try:
        vf_date = datetime.strptime(vf_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        vf_date = "N/A"

    # Extract vendor, items, and total
    vendor = vf_data.get("vendor", {}).get("name", "Unknown Vendor")
    vf_items = [item.get("description", "Unknown Item") for item in vf_data.get("line_items", [])]
    total = vf_data.get("total", 0.0)

    # Determine the category
    categories_str = ", ".join(categories)
    category = get_category(vendor, categories_str)

    # Fetch vendor logo from Clearbit
    def get_logo_url(vendor_name):
        try:
            domain = vendor_name.lower().replace(" ", "") + ".com"
            response = requests.get(f"https://logo.clearbit.com/{domain}")
            if response.status_code == 200:
                return response.url
        except requests.RequestException as e:
            print(f"Error fetching logo for {vendor_name}: {e}")
        return ""  # Return an empty string if the logo is not found

    logo_url = get_logo_url(vendor)
    print("Vendor Logo URL:", logo_url)  # Debug: log the logo URL

    # Prepare the receipt data
    receipt_data = {
        "id": vf_data.get("id", "N/A"),
        "vendor": vendor,
        "total": total,
        "category": category,
        "date": vf_date,
        "items": vf_items,
        "logoUrl": logo_url,
    }

    print("Processed Receipt Data:", receipt_data)  # Debug: log the final receipt data
    return jsonify(receipt_data), 201


@api_bp.route("/update-receipt", methods=["PUT"])
def update_receipt():
    data = request.get_json()
    receipt_id = data.get("id")
    new_category = data.get("category")

    # Validate the input
    if not receipt_id or not new_category:
        return jsonify({"error": "Invalid data. Receipt ID and category are required."}), 400

    # Simulate updating the receipt (replace with database logic in a real app)
    updated_receipt = {
        "id": receipt_id,
        "category": new_category,
        "message": "Category updated successfully",
    }

    print("Updated Receipt:", updated_receipt)  # Debug: log the update
    return jsonify(updated_receipt), 200
