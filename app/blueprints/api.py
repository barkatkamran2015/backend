@api_bp.route("/process-receipt", methods=['POST'])
def process_receipt():
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded or invalid file."}), 400

    categories = request.form.get('categories', '[]')
    try:
        categories = json.loads(categories)
        if not isinstance(categories, list):
            raise ValueError("Categories must be a list")
    except (ValueError, json.JSONDecodeError):
        return jsonify({"error": "Invalid categories format. Must be a JSON list."}), 400

    # Prepare Veryfi request
    files = {'file': (file.filename, file, file.content_type)}
    headers = {
        'Accept': 'application/json',
        'Client-Id': veryfi_config['client_id'],
        'Authorization': f"apikey {veryfi_config['username']}:{veryfi_config['api_key']}"
    }

    try:
        vf_response = requests.post(veryfi_config['api_url'], headers=headers, files=files)
        vf_response.raise_for_status()
        vf_data = vf_response.json()
    except requests.RequestException as e:
        print(f"Error with VeryFI API: {e}")
        return jsonify({"error": "Error processing the receipt. Please try again later."}), 500
    except ValueError as e:
        print(f"Error parsing VeryFI response: {e}")
        return jsonify({"error": "Invalid response from receipt processing service."}), 500

    vendor = vf_data.get('vendor', {}).get('name', "Unknown Vendor")
    logo_url = get_logo_url(vendor) if vendor != "Unknown Vendor" else ''
    vf_date = vf_data.get('date', "N/A")
    try:
        vf_date = datetime.strptime(vf_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        vf_date = "N/A"

    vf_items = [item.get('description', 'Unknown Item') for item in vf_data.get('line_items', [])]
    category = get_category(vendor, ", ".join(categories))

    receipt_data = {
        'id': vf_data.get('id', 'N/A'),
        'vendor': vendor,
        'total': vf_data.get('total', 0.0),
        'category': category,
        'date': vf_date,
        'items': vf_items,
        'logoUrl': logo_url
    }

    return jsonify(receipt_data), 201
