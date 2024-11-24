@api_bp.route("/process-receipt", methods=['POST'])
def process_receipt():
    try:
        print("Request received at /api/process-receipt")  # Log route hit
        print("Headers:", request.headers)  # Log request headers
        print("Form data:", request.form)  # Log form data
        print("Files:", request.files)  # Log uploaded files

        # Check if 'file' is in the request
        if 'file' not in request.files:
            print("No file found in the request")
            return jsonify({"error": "No file provided"}), 400

        # Get the uploaded file
        file = request.files['file']
        print("File received:", file.filename)  # Debug: Log the filename

        # Get categories from the request form data and parse it as a list
        categories = json.loads(request.form.get('categories', '[]'))

        # Set parameters for forwarding image to VeryFI
        files = {
            'file': (file.filename, file, file.content_type)
        }

        vf_client_id = veryfi_config['client_id']
        vf_username = veryfi_config['username']
        vf_api_key = veryfi_config['api_key']
        vf_api_url = veryfi_config['api_url']

        headers = {
            'Accept': 'application/json',
            'Client-Id': vf_client_id,
            'Authorization': f"apikey {vf_username}:{vf_api_key}"
        }

        # Send the file to VeryFI to process
        vf_response = requests.post(vf_api_url, headers=headers, files=files)
        print("VeryFI API Response:", vf_response.status_code, vf_response.text)

        # Parse the response
        vf_data = vf_response.json()
        print("Parsed VeryFI response:", vf_data)

        # Check if 'date' is present and handle missing or malformed dates
        if 'date' in vf_data and vf_data['date']:
            try:
                vf_date = datetime.strptime(vf_data['date'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            except ValueError:
                vf_date = "N/A"  # Handle date parsing error
        else:
            vf_date = "N/A"  # Default if date is missing or invalid

        # Extract line items
        vf_items = []
        for item in vf_data.get('line_items', []):
            vf_items.append(item['description'])

        # Extract vendor and categorize
        vendor = vf_data['vendor']['name'] if 'vendor' in vf_data and 'name' in vf_data['vendor'] else "Unknown Vendor"
        categories = ", ".join(categories)
        category = get_category(vendor, categories)

        # Function to fetch logo URL from an external service (e.g., Clearbit Logo API)
        def get_logo_url(vendor_name):
            try:
                domain = vendor_name.lower().replace(' ', '') + '.com'
                response = requests.get(f'https://logo.clearbit.com/{domain}')
                if response.status_code == 200:
                    return response.url  # Return the URL if the request is successful
            except requests.RequestException as e:
                print(f"Error fetching logo for {vendor_name}: {e}")
            return ''  # Return an empty string if the logo is not found or an error occurs

        # Get the logo URL for the vendor
        logo_url = get_logo_url(vendor)

        # Debug: print constructed logo URL
        print("Constructed logo URL:", logo_url)

        receipt_data = {
            'id': vf_data.get('id', 'N/A'),  # Ensure an ID is included for frontend use
            'vendor': vendor,
            'total': vf_data['total'] if 'total' in vf_data else 0.0,
            'category': category,
            'date': vf_date,
            'items': vf_items,
            'logoUrl': logo_url  # Add the logo URL to the response
        }

        print("Final Receipt Data:", receipt_data)  # Debug: print final receipt data

        return jsonify(receipt_data), 201

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
