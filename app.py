from flask import Flask, render_template, request, send_from_directory
import requests
import pandas as pd
from datetime import datetime

app = Flask(__name__)

base_url = 'https://erpv14.electrolabgroup.com/'
endpoint = 'api/resource/Sales Order'

headers = {
    'Authorization': 'token 3ee8d03949516d0:6baa361266cf807'
}

def retrieve_data(name):
    limit_start = 0
    limit_page_length = 1000
    all_data = []

    while True:
        params = {
            'fields': '["name","customer","items.item_code","items.item_name","items.serial_no","items.item_name","territory","items.qty","address_display","shipping_address","shipping_address_name","po_no","po_date","freight_term","payment_terms_template","currency","items.rate","items.amount","freight_amt","packing_charges","total_net_weight","items.gst_hsn_code","items.uom","total_net_weight","net_total","taxes.account_head","taxes.tax_amount","taxes.total"]',
            'limit_start': limit_start,
            'limit_page_length': limit_page_length,
            'filters': f'[["name", "in", "{name}"]]'
        }

        response = requests.get(base_url + endpoint, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            current_page_data = data.get('data', [])

            if not current_page_data:
                break  # No more data to fetch

            all_data.extend(current_page_data)
            limit_start += limit_page_length
        else:
            print(f"Error: {response.status_code}")
            break

    if all_data:
        so_df = pd.DataFrame(all_data)
        # Sort the DataFrame by the 'amount' column in descending order
        so_df = so_df.sort_values(by='amount', ascending=False)
        so_df['qty'] = so_df['qty'].round(0).astype(int)

        return so_df
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    item_names = []
    certificate_content = None
    shipping_content = None
    if request.method == 'POST':
        name = request.form.get('name', '')
        if name.strip():
            so_df = retrieve_data(name)
            if so_df is not None:
                item_names = so_df['item_name'].unique().tolist()
                if 'print_certificate' in request.form:
                    selected_item_name = request.form.get('selected_item_name', '')
                    if selected_item_name:
                        selected_row = so_df[so_df['item_name'] == selected_item_name].iloc[0]
                        item_code = selected_row['item_code']
                        serial_no = selected_row['serial_no']
                        qty = selected_row['qty']
                        territory = selected_row['territory']
                        customer = selected_row['customer']
                        certificate_content = render_template('certificate.html', item_name=selected_item_name,
                                                              item_code=item_code,
                                                              serial_no=serial_no, qty=qty, territory=territory,
                                                              customer=customer)
                    else:
                        certificate_content = 'Item name is required to print the certificate.'
                elif 'print_shipping_list' in request.form:
                    shipping_content = render_template('shipping_list.html', items=so_df.to_dict(orient='records'))

                elif 'print_ci' in request.form:
                    shipping_content = render_template('commercial_invoice.html', items=so_df.to_dict(orient='records'))

                elif 'print_pl' in request.form:
                    shipping_content = render_template('packing_list.html', items=so_df.to_dict(orient='records'))

                elif 'print_dgr' in request.form:
                    shipping_content = render_template('non_dgr.html', items=so_df.to_dict(orient='records'))

                elif 'print_scomet' in request.form:
                    shipping_content = render_template('non_scomet.html', items=so_df.to_dict(orient='records'))

                return render_template('index.html', item_names=item_names, certificate_content=certificate_content,
                                       shipping_content=shipping_content, name=name)








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
                                                  serial_no=serial_no, qty=qty, territory=territory, customer=customer)
            return render_template('index.html', item_names=item_names, certificate_content=certificate_content,
                                   name=name)
        else:
            return 'Item name is required to print the certificate.'
    else:
        return f'Request failed to retrieve data for {name}.'



@app.route('/print_sticker', methods=['POST'])
def print_sticker():
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
            po_no = selected_row['po_no']
            sales_order = selected_row['name']

            certificate_content = render_template('sticker.html', item_name=selected_item_name, item_code=item_code,
                                                  serial_no=serial_no, qty=qty, territory=territory, customer=customer,po_no = po_no,sales_order = sales_order)
            return render_template('index.html', item_names=item_names, certificate_content=certificate_content,
                                   name=name)
        else:
            return 'Item name is required to print the certificate.'
    else:
        return f'Request failed to retrieve data for {name}.'





@app.route('/print_ci', methods=['POST'])
def print_commercial_invoice():
    # Get shipping address from form data
    name = request.form.get('name', '')
    # Get shipping address from form data
    so_df = retrieve_data(name)

    item_names = []  # Initialize item_names as empty list

    if so_df is not None:
        item_names = so_df['item_name'].unique().tolist()

        sale_charges = so_df[["name", "account_head", "tax_amount", "total"]]
        sale_charges = sale_charges.sort_values(by='total', ascending=True)
        so_df = so_df[
            ["name", "customer", "item_code", "item_name", "serial_no", "item_name", "territory", "qty",
             "address_display",
             "shipping_address", "shipping_address_name", "po_no", "po_date", "freight_term", "payment_terms_template",
             "currency", "rate", "amount", "freight_amt", "packing_charges", "total_net_weight", "gst_hsn_code", "uom",
             "total_net_weight", "net_total"]]

        # Drop duplicate rows
        so_df = so_df.drop_duplicates()
        items = so_df.to_dict(orient='records')
        charges = sale_charges.to_dict(orient='records')

        unique_currency = so_df['currency'].unique().tolist()
        # Pass the first customer name to the template
        currency = unique_currency[0] if unique_currency else ""

        unique_shipname = so_df['customer'].unique().tolist()
        # Pass the first customer name to the template
        shipping_address_name = unique_shipname[0] if unique_shipname else ""

        unique_customers = so_df['customer'].unique().tolist()
        # Pass the first customer name to the template
        customer = unique_customers[0] if unique_customers else ""

        unique_shipping = so_df['shipping_address'].unique().tolist()
        # Pass the first customer name to the template
        shipping_address = "<br>".join(unique_shipping) if unique_shipping else ""

        unique_address = so_df['address_display'].unique().tolist()
        # Pass the first customer name to the template
        customer_address = "<br>".join(unique_address) if unique_address else ""

        unique_payment_term = so_df['payment_terms_template'].unique().tolist()
        unique_payment_term  = [str(term) for term in unique_payment_term]
        # Pass the first customer name to the template
        payment_terms_template = "<br>".join(unique_payment_term) if unique_payment_term else ""

        unique_freight_term = so_df['freight_term'].unique().tolist()
        # Pass the first customer name to the template
        freight_term = "<br>".join(unique_freight_term) if unique_freight_term else ""

        unique_po_no = so_df['po_no'].unique().tolist()
        # Pass the first customer name to the template
        po_no = "<br>".join(unique_po_no) if unique_po_no else ""

        unique_territory = so_df['territory'].unique().tolist()
        # Pass the first customer name to the template
        territory = "<br>".join(unique_territory) if unique_territory else ""




        unique_packing_charges = so_df['packing_charges'].unique().tolist()
        # Pass the first customer name to the template
        packing_charges = "<br>".join(unique_packing_charges) if unique_packing_charges else ""

        ci_content = render_template('commercial_invoice.html', items=items, currency=currency,charges= charges,
                                     customer=customer, shipping_address=shipping_address,
                                     customer_address=customer_address, shipping_address_name=shipping_address_name,po_no= po_no,payment_terms_template = payment_terms_template,freight_term=freight_term,territory=territory,packing_charges = packing_charges)

        return render_template('index.html', item_names=item_names, ci_content=ci_content, name=name)
    else:
        return f'Request failed to retrieve data for {name}.'


@app.route('/print_si', methods=['POST'])
def print_shipping_list():
    # Get shipping address from form data
    name = request.form.get('name', '')
    # Get shipping address from form data
    so_df = retrieve_data(name)
    item_names = []  # Initialize item_names as empty list

    if so_df is not None:
        item_names = so_df['item_name'].unique().tolist()

        sale_charges = so_df[["name", "account_head", "tax_amount", "total"]]
        sale_charges = sale_charges.sort_values(by='total', ascending=True)

        so_df = so_df[
            ["name", "customer", "item_code", "item_name", "serial_no", "item_name", "territory", "qty",
             "address_display",
             "shipping_address", "shipping_address_name", "po_no", "po_date", "freight_term", "payment_terms_template",
             "currency", "rate", "amount", "freight_amt", "packing_charges", "total_net_weight", "gst_hsn_code", "uom",
             "total_net_weight", "net_total"]]

        # Drop duplicate rows
        so_df = so_df.drop_duplicates()
        items = so_df.to_dict(orient='records')
        charges = sale_charges.to_dict(orient='records')

        unique_currency = so_df['currency'].unique().tolist()
        # Pass the first customer name to the template
        currency = unique_currency[0] if unique_currency else ""


        unique_shipname = so_df['customer'].unique().tolist()
        # Pass the first customer name to the template
        shipping_address_name = unique_shipname[0] if unique_shipname else ""

        unique_customers = so_df['customer'].unique().tolist()
        # Pass the first customer name to the template
        customer = unique_customers[0] if unique_customers else ""

        unique_shipping = so_df['shipping_address'].unique().tolist()
        # Pass the first customer name to the template
        shipping_address = "<br>".join(unique_shipping) if unique_shipping else ""

        unique_address = so_df['address_display'].unique().tolist()
        # Pass the first customer name to the template
        customer_address = "<br>".join(unique_address) if unique_address else ""

        unique_payment_term = so_df['payment_terms_template'].unique().tolist()
        unique_payment_term = [str(term) for term in unique_payment_term]
        # Pass the first customer name to the template
        payment_terms_template = "<br>".join(unique_payment_term) if unique_payment_term else ""

        unique_freight_term = so_df['freight_term'].unique().tolist()
        # Pass the first customer name to the template
        freight_term = "<br>".join(unique_freight_term) if unique_payment_term else ""

        unique_po_no = so_df['po_no'].unique().tolist()
        # Pass the first customer name to the template
        po_no = "<br>".join(unique_po_no) if unique_po_no else ""

        unique_territory = so_df['territory'].unique().tolist()
        # Pass the first customer name to the template
        territory = "<br>".join(unique_territory) if unique_territory else ""



        unique_packing_charges = so_df['packing_charges'].unique().tolist()
        # Pass the first customer name to the template
        packing_charges = "<br>".join(unique_packing_charges) if unique_packing_charges else ""

        unique_hsn_code = so_df['gst_hsn_code'].unique().tolist()
        # Pass the first hsn_code to the template
        hsn_code = "<br>".join(unique_hsn_code) if unique_hsn_code else " "



        si_content = render_template('shipping_list.html', charges= charges,items=items, currency=currency,
                                     customer=customer, shipping_address=shipping_address,
                                     customer_address=customer_address, shipping_address_name=shipping_address_name,po_no= po_no,payment_terms_template = payment_terms_template,freight_term=freight_term,territory=territory,packing_charges = packing_charges,hsn_code=hsn_code)

        return render_template('index.html', item_names=item_names, shipping_content=si_content, name=name)
    else:
        return f'Request failed to retrieve data for {name}.'



@app.route('/packing_list', methods=['POST'])
def packing_list_spares():
    # Get shipping address from form data
    name = request.form.get('name', '')
    # Get shipping address from form data
    so_df = retrieve_data(name)
    item_names = []  # Initialize item_names as empty list

    if so_df is not None:
        item_names = so_df['item_name'].unique().tolist()

        sale_charges = so_df[["name", "account_head", "tax_amount", "total"]]
        so_df = so_df[
            ["name", "customer", "item_code", "item_name", "serial_no", "item_name", "territory", "qty",
             "address_display",
             "shipping_address", "shipping_address_name", "po_no", "po_date", "freight_term", "payment_terms_template",
             "currency", "rate", "amount", "freight_amt", "packing_charges", "total_net_weight", "gst_hsn_code", "uom",
             "total_net_weight", "net_total"]]

        # Drop duplicate rows
        so_df = so_df.drop_duplicates()
        items = so_df.to_dict(orient='records')
        charges = sale_charges.to_dict(orient='records')
        currency = so_df['currency']  # Assuming you have a currency variable


        unique_shipname = so_df['customer'].unique().tolist()
        # Pass the first customer name to the template
        shipping_address_name = unique_shipname[0] if unique_shipname else ""

        unique_customers = so_df['customer'].unique().tolist()
        # Pass the first customer name to the template
        customer = unique_customers[0] if unique_customers else ""

        unique_shipping = so_df['shipping_address'].unique().tolist()
        # Pass the first customer name to the template
        shipping_address = "<br>".join(unique_shipping) if unique_shipping else ""

        unique_address = so_df['address_display'].unique().tolist()
        # Pass the first customer name to the template
        customer_address = "<br>".join(unique_address) if unique_address else ""

        unique_payment_term = so_df['payment_terms_template'].unique().tolist()
        unique_payment_term = [str(term) for term in unique_payment_term]
        # Pass the first customer name to the template
        payment_terms_template = "<br>".join(unique_payment_term) if unique_payment_term else ""

        unique_freight_term = so_df['freight_term'].unique().tolist()
        # Pass the first customer name to the template
        freight_term = "<br>".join(unique_freight_term) if unique_payment_term else ""

        unique_po_no = so_df['po_no'].unique().tolist()
        # Pass the first customer name to the template
        po_no = "<br>".join(unique_po_no) if unique_po_no else ""

        unique_territory = so_df['territory'].unique().tolist()
        # Pass the first customer name to the template
        territory = "<br>".join(unique_territory) if unique_territory else ""



        unique_packing_charges = so_df['packing_charges'].unique().tolist()
        # Pass the first customer name to the template
        packing_charges = "<br>".join(unique_packing_charges) if unique_packing_charges else ""



        pl_content = render_template('packing_list.html', items=items, currency=currency,
                                     customer=customer, shipping_address=shipping_address,
                                     customer_address=customer_address, shipping_address_name=shipping_address_name,po_no= po_no,payment_terms_template = payment_terms_template,freight_term=freight_term,territory=territory,packing_charges = packing_charges)

        return render_template('index.html', item_names=item_names, pl_content=pl_content, name=name)
    else:
        return f'Request failed to retrieve data for {name}.'




@app.route('/packing_list_spares', methods=['POST'])
def packing_list():
    # Get shipping address from form data
    name = request.form.get('name', '')
    # Get shipping address from form data
    so_df = retrieve_data(name)
    item_names = []  # Initialize item_names as empty list

    if so_df is not None:
        item_names = so_df['item_name'].unique().tolist()

        sale_charges = so_df[["name", "account_head", "tax_amount", "total"]]
        so_df = so_df[
            ["name", "customer", "item_code", "item_name", "serial_no", "item_name", "territory", "qty",
             "address_display",
             "shipping_address", "shipping_address_name", "po_no", "po_date", "freight_term", "payment_terms_template",
             "currency", "rate", "amount", "freight_amt", "packing_charges", "total_net_weight", "gst_hsn_code", "uom",
             "total_net_weight", "net_total"]]

        # Drop duplicate rows
        so_df = so_df.drop_duplicates()
        items = so_df.to_dict(orient='records')
        charges = sale_charges.to_dict(orient='records')
        currency = so_df['currency']  # Assuming you have a currency variable

        unique_name = so_df['name'].unique().tolist()
        # Pass the first customer name to the template
        sales_order = unique_name[0] if unique_name else ""

        unique_shipname = so_df['customer'].unique().tolist()
        # Pass the first customer name to the template
        shipping_address_name = unique_shipname[0] if unique_shipname else ""

        unique_customers = so_df['customer'].unique().tolist()
        # Pass the first customer name to the template
        customer = unique_customers[0] if unique_customers else ""

        unique_shipping = so_df['shipping_address'].unique().tolist()
        # Pass the first customer name to the template
        shipping_address = "<br>".join(unique_shipping) if unique_shipping else ""

        unique_address = so_df['address_display'].unique().tolist()
        # Pass the first customer name to the template
        customer_address = "<br>".join(unique_address) if unique_address else ""

        unique_payment_term = so_df['payment_terms_template'].unique().tolist()
        unique_payment_term = [str(term) for term in unique_payment_term]
        # Pass the first customer name to the template
        payment_terms_template = "<br>".join(unique_payment_term) if unique_payment_term else ""

        unique_freight_term = so_df['freight_term'].unique().tolist()
        # Pass the first customer name to the template
        freight_term = "<br>".join(unique_freight_term) if unique_payment_term else ""

        unique_po_no = so_df['po_no'].unique().tolist()
        # Pass the first customer name to the template
        po_no = "<br>".join(unique_po_no) if unique_po_no else ""

        unique_territory = so_df['territory'].unique().tolist()
        # Pass the first customer name to the template
        territory = "<br>".join(unique_territory) if unique_territory else ""

        current_date = datetime.now().strftime("%d-%m-%Y")

        unique_packing_charges = so_df['packing_charges'].unique().tolist()
        # Pass the first customer name to the template
        packing_charges = "<br>".join(unique_packing_charges) if unique_packing_charges else ""

        unique_salesorder = so_df['name'].unique().tolist()
        # Pass the first customer name to the template
        sales_order = unique_salesorder[0] if unique_salesorder else ""


        pl_content_spares = render_template('packing_list_spares.html', items=items, currency=currency,
                                     customer=customer, shipping_address=shipping_address,
                                     customer_address=customer_address, shipping_address_name=shipping_address_name,po_no= po_no,payment_terms_template = payment_terms_template,freight_term=freight_term,territory=territory,packing_charges = packing_charges,current_date=current_date,sales_order=sales_order)

        return render_template('index.html', item_names=item_names, pl_content_spares=pl_content_spares, name=name)
    else:
        return f'Request failed to retrieve data for {name}.'


@app.route('/non_dgr', methods=['POST'])
def non_dgr():
    # Get shipping address from form data
    name = request.form.get('name', '')
    # Get shipping address from form data
    so_df = retrieve_data(name)
    item_names = []  # Initialize item_names as empty list

    if so_df is not None:
        item_names = so_df['item_name'].unique().tolist()

        sale_charges = so_df[["name", "account_head", "tax_amount", "total"]]
        so_df = so_df[
            ["name", "customer", "item_code", "item_name", "serial_no", "item_name", "territory", "qty",
             "address_display",
             "shipping_address", "shipping_address_name", "po_no", "po_date", "freight_term", "payment_terms_template",
             "currency", "rate", "amount", "freight_amt", "packing_charges", "total_net_weight", "gst_hsn_code", "uom",
             "total_net_weight", "net_total"]]

        # Drop duplicate rows
        so_df = so_df.drop_duplicates()
        items = so_df.to_dict(orient='records')
        charges = sale_charges.to_dict(orient='records')
        currency = so_df['currency']  # Assuming you have a currency variable



        unique_shipname = so_df['customer'].unique().tolist()
        # Pass the first customer name to the template
        shipping_address_name = unique_shipname[0] if unique_shipname else ""

        unique_customers = so_df['customer'].unique().tolist()
        # Pass the first customer name to the template
        customer = unique_customers[0] if unique_customers else ""

        unique_shipping = so_df['shipping_address'].unique().tolist()
        # Pass the first customer name to the template
        shipping_address = "<br>".join(unique_shipping) if unique_shipping else ""

        unique_address = so_df['address_display'].unique().tolist()
        # Pass the first customer name to the template
        customer_address = "<br>".join(unique_address) if unique_address else ""

        unique_payment_term = so_df['payment_terms_template'].unique().tolist()
        unique_payment_term = [str(term) for term in unique_payment_term]
        # Pass the first customer name to the template
        payment_terms_template = "<br>".join(unique_payment_term) if unique_payment_term else ""

        unique_freight_term = so_df['freight_term'].unique().tolist()
        # Pass the first customer name to the template
        freight_term = "<br>".join(unique_freight_term) if unique_payment_term else ""

        unique_po_no = so_df['po_no'].unique().tolist()
        # Pass the first customer name to the template
        po_no = "<br>".join(unique_po_no) if unique_po_no else ""

        unique_territory = so_df['territory'].unique().tolist()
        # Pass the first customer name to the template
        territory = "<br>".join(unique_territory) if unique_territory else ""



        unique_packing_charges = so_df['packing_charges'].unique().tolist()
        # Pass the first customer name to the template
        packing_charges = "<br>".join(unique_packing_charges) if unique_packing_charges else ""



        nondgr_content = render_template('non_dgr.html', items=items, currency=currency,
                                     customer=customer, shipping_address=shipping_address,
                                     customer_address=customer_address, shipping_address_name=shipping_address_name,po_no= po_no,payment_terms_template = payment_terms_template,freight_term=freight_term,territory=territory,packing_charges = packing_charges)

        return render_template('index.html', item_names=item_names, nondgr_content=nondgr_content, name=name)
    else:
        return f'Request failed to retrieve data for {name}.'


@app.route('/scomet_page', methods=['POST'])
def scomet():
    # Get shipping address from form data
    name = request.form.get('name', '')
    # Get shipping address from form data
    so_df = retrieve_data(name)
    item_names = []  # Initialize item_names as empty list

    if so_df is not None:
        item_names = so_df['item_name'].unique().tolist()

        sale_charges = so_df[["name", "account_head", "tax_amount", "total"]]
        so_df = so_df[
            ["name", "customer", "item_code", "item_name", "serial_no", "item_name", "territory", "qty",
             "address_display",
             "shipping_address", "shipping_address_name", "po_no", "po_date", "freight_term", "payment_terms_template",
             "currency", "rate", "amount", "freight_amt", "packing_charges", "total_net_weight", "gst_hsn_code", "uom",
             "total_net_weight", "net_total"]]

        # Drop duplicate rows
        so_df = so_df.drop_duplicates()
        items = so_df.to_dict(orient='records')
        charges = sale_charges.to_dict(orient='records')
        currency = so_df['currency']  # Assuming you have a currency variable


        unique_shipname = so_df['customer'].unique().tolist()
        # Pass the first customer name to the template
        shipping_address_name = unique_shipname[0] if unique_shipname else ""

        unique_customers = so_df['customer'].unique().tolist()
        # Pass the first customer name to the template
        customer = unique_customers[0] if unique_customers else ""

        unique_shipping = so_df['shipping_address'].unique().tolist()
        # Pass the first customer name to the template
        shipping_address = "<br>".join(unique_shipping) if unique_shipping else ""

        unique_address = so_df['address_display'].unique().tolist()
        # Pass the first customer name to the template
        customer_address = "<br>".join(unique_address) if unique_address else ""

        unique_payment_term = so_df['payment_terms_template'].unique().tolist()
        unique_payment_term = [str(term) for term in unique_payment_term]
        # Pass the first customer name to the template
        payment_terms_template = "<br>".join(unique_payment_term) if unique_payment_term else ""

        unique_freight_term = so_df['freight_term'].unique().tolist()
        # Pass the first customer name to the template
        freight_term = "<br>".join(unique_freight_term) if unique_payment_term else ""

        unique_po_no = so_df['po_no'].unique().tolist()
        # Pass the first customer name to the template
        po_no = "<br>".join(unique_po_no) if unique_po_no else ""

        unique_territory = so_df['territory'].unique().tolist()
        # Pass the first customer name to the template
        territory = "<br>".join(unique_territory) if unique_territory else ""



        unique_packing_charges = so_df['packing_charges'].unique().tolist()
        # Pass the first customer name to the template
        packing_charges = "<br>".join(unique_packing_charges) if unique_packing_charges else ""



        scomet_content = render_template('non_scomet.html', items=items, currency=currency,
                                     customer=customer, shipping_address=shipping_address,
                                     customer_address=customer_address, shipping_address_name=shipping_address_name,po_no= po_no,payment_terms_template = payment_terms_template,freight_term=freight_term,territory=territory,packing_charges = packing_charges)

        return render_template('index.html', item_names=item_names, scomet_content=scomet_content, name=name)
    else:
        return f'Request failed to retrieve data for {name}.'




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
