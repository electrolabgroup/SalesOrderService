from flask import Flask, render_template, request, send_from_directory
import requests
import pandas as pd
app = Flask(__name__)

base_url = 'https://erpv14.electrolabgroup.com/'
endpoint = 'api/resource/Sales Order'

headers = {
    'Authorization': 'token 3ee8d03949516d0:bec5931806c7cc6'
}




def retrieve_data(name):
    params = {
        'fields': '["name","customer","items.item_code","items.item_name","items.serial_no","items.item_name","territory","items.qty"]',
        'limit_start': 0,
        'limit_page_length': 1000,
        'filters': f'[["name", "in", "{name}"]]'
    }

    response = requests.get(base_url + endpoint, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        all_data = data['data']
        so_df = pd.DataFrame(all_data)
        #so_df = so_df[so_df['serial_no'].notna() & (so_df['serial_no'] != '')]
        return so_df
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    item_names = []  # Initialize item_names as empty list
    certificate_content = None  # Initialize certificate_content as None
    if request.method == 'POST':
        name = request.form.get('name', '')
        if name.strip():
            so_df = retrieve_data(name)
            if so_df is not None:
                item_names = so_df['item_name'].unique().tolist()
                if 'print_certificate' in request.form:
                    selected_item_name = request.form.get('selected_item_name', '')  # Get selected item name
                    if selected_item_name:  # Check if selected item name is not empty
                        selected_row = so_df[so_df['item_name'] == selected_item_name].iloc[0]
                        item_code = selected_row['item_code']
                        serial_no = selected_row['serial_no']
                        qty = selected_row['qty']
                        territory = selected_row['territory']
                        certificate_content = render_template('certificate.html', item_name=selected_item_name, item_code=item_code,
                                               serial_no=serial_no, qty=qty, territory=territory)
                    else:
                        certificate_content = 'Item name is required to print the certificate.'
                return render_template('index.html', item_names=item_names, certificate_content=certificate_content)
            else:
                return f'Request failed to retrieve data for {name}.'
        else:
            return 'Name field is required.'

    return render_template('index.html', item_names=item_names, certificate_content=certificate_content)


@app.route('/print_certificate', methods=['POST'])
def print_certificate():
    selected_item_name = request.form.get('selected_item_name', '')
    name = request.form.get('name', '')
    so_df = retrieve_data(name)
    item_names = []  # Initialize item_names as empty list
    if so_df is not None:
        item_names = so_df['item_name'].unique().tolist()
        if selected_item_name:
            selected_row = so_df[so_df['item_name'] == selected_item_name].iloc[0]
            item_code = selected_row['item_code']
            serial_no = selected_row['serial_no']
            qty = selected_row['qty']
            territory = selected_row['territory']
            customer = selected_row['customer']
            certificate_content = render_template('certificate.html', item_name=selected_item_name, item_code=item_code,
                                   serial_no=serial_no, qty=qty, territory=territory, customer = customer)
            return render_template('index.html', item_names=item_names, certificate_content=certificate_content)
        else:
            return 'Item name is required to print the certificate.'
    else:
        return f'Request failed to retrieve data for {name}.'







if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
