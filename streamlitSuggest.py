import streamlit as st
from datetime import datetime
import pandas as pd

st.set_page_config(layout="wide")
# Initialize session state variables
if 'show_transaction' not in st.session_state:
    st.session_state.show_transaction = True
if 'show_invoice_form' not in st.session_state:
    st.session_state.show_invoice_form = False
if 'show_journal_form' not in st.session_state:
    st.session_state.show_journal_form = False


# Function to reset the forms display
def reset_forms():
    st.session_state.show_invoice_form = False
    st.session_state.show_journal_form = False
    st.session_state.show_transaction = False 

# Function to handle new transaction button
def handle_new_transaction():
    st.session_state.show_transaction = False
    reset_forms()

# Function to display invoice form
def show_invoice_form():
    reset_forms()
    st.session_state.show_invoice_form = True
invoice_df = None
journal_df = None
def autofill_invoice_data(invoice_df):

    if invoice_df is not None:
        # Collect form data

        invoice_df = invoice_df.applymap(lambda x: str(x) if pd.notnull(x) else "")

        amount = st.session_state.get('transaction_amount', "")
        # amount = float(amount) if amount is not None else None

        description = st.session_state.get('transaction_description', "")
        reference = st.session_state.get('transaction_reference', "")
        payer_payee = st.session_state.get('transaction_payer_payee', "")


        # The query should be sL or new sL null, still match
        query = ((invoice_df['net_amount'] == amount) | (invoice_df['net_amount'] == "") | (amount == "")) & \
                ((invoice_df['bse_description'] == description) | (invoice_df['bse_description'] == "") | (description == "")) & \
                ((invoice_df['ext_reference'] == reference) | (invoice_df['ext_reference'] == "") | (reference == "")) & \
                ((invoice_df['ext_contact_name'] == payer_payee) | (invoice_df['ext_contact_name'] == "") | (payer_payee == ""))
        

        matched_rows = invoice_df.loc[query]
        if not matched_rows.empty:
            # Assuming you want to use the first match if there are multiple
            match = matched_rows.iloc[0]
            # Now, you can autofill other parts of your application based on this match
            st.session_state['tax_profile_name'] = match['tax_profile_name']
            st.session_state['InvoicepayMeth'] = match['payment_method']
            st.session_state['tax_profile_tax_type_name'] = match['tax_profile_tax_type_name']
            st.session_state['custom_fields'] = match['custom_fields']
            st.session_state['InvoiceContact'] = match['name']
            # st.session_state['InvoiceDescript'] = match['description']
            st.session_state['invoiceaccount'] = match['account_resource_id']
            st.session_state['tax_profile_vat_value'] = match['tax_profile_vat_value']
            
        else:
            st.error("No matching transaction found in the uploaded Excel file.")

def autofill_journal_data(journal_df):
    if journal_df is not None:

        journal_df = journal_df.applymap(lambda x: str(x) if pd.notnull(x) else "")
        # Collect form data
        amount = st.session_state.get('transaction_amount', "")
        description = st.session_state.get('transaction_description', "")
        reference = st.session_state.get('transaction_reference', "")
        payer_payee = st.session_state.get('transaction_payer_payee', "")

        # journal_df['business_transaction_reference'] = journal_df['business_transaction_reference'].apply(lambda x: str(x) if pd.notnull(x) else "")
        # journal_df['name_str'] = journal_df['name'].apply(lambda x: str(x) if pd.notnull(x) else "")

        query = ((journal_df['net_amount'] == amount) | (journal_df['net_amount'] == "") | (amount == "")) & \
                ((journal_df['bse_description'] == description) | (journal_df['bse_description'] == "") | (description == "")) & \
                ((journal_df['ext_reference'] == reference) | (journal_df['ext_reference'] == "") | (reference == "")) & \
                ((journal_df['ext_contact_name'] == payer_payee) | (journal_df['ext_contact_name'] == "") | (payer_payee == ""))



        matched_rows = journal_df.loc[query]

        if not matched_rows.empty:
            # Assuming you want to use the first match if there are multiple
            match = matched_rows.iloc[0]

            
            st.session_state['JounralReference'] = match['journal_reference']
            st.session_state['jorunalcontact'] = match['journal_contact']
            st.session_state['journalaccount'] = match['account_resource_id']
            st.session_state['journaldescription'] = match['description']
            st.session_state['journalAmount'] = match['amount']
            st.session_state['taxJournal'] = match['tax_profile_name']

        else:
            st.error("No matching journal entry found in the uploaded Excel file.")


def display_journal_form():
    reset_forms()
    st.session_state.show_journal_form = True

    st.text_input('Journal Reference', value='Cash-in Transaction', key='JounralReference')
    st.date_input('Date', value=st.session_state.get('date', datetime.date(2024, 2, 26)))
    st.text_input('Contact', key='jorunalcontact')
    st.text_input('Tracking Tags', key='tracktagsjournal')
    st.text_area('Internal Notes', value='Add notes for your internal team', key='internalnotesjounral')

    # Handle the dynamic addition of new lines for the journal entry
    if 'journal_lines' not in st.session_state:
        st.session_state.journal_lines = [{'account': '', 'description': '', 'debits': 0.00, 'credits': 199.00}]

    for i, line in enumerate(st.session_state.journal_lines):
        cols = st.columns([3, 7, 2, 2])
        with cols[0]:
            account_key = f'account_{i}'
            line['account'] = st.selectbox(f"Account {i+1}", ['Credit Suisse (00071)', 'Account 2', 'Account 3'], key=account_key)
        with cols[1]:
            description_key = f'description_{i}'
            line['description'] = st.text_input(f"Description {i+1}", key=description_key)
        with cols[2]:
            debits_key = f'debits_{i}'
            line['debits'] = st.number_input(f"Debits {i+1}", min_value=0.00, key=debits_key)
        with cols[3]:
            credits_key = f'credits_{i}'
            line['credits'] = st.number_input(f"Credits {i+1}", min_value=0.00, key=credits_key)

    if st.button('Add New Line'):
        st.session_state.journal_lines.append({'account': '', 'description': '', 'debits': 0.00, 'credits': 0.00})
        

    # Display totals
    total_debits = sum(line['debits'] for line in st.session_state.journal_lines)
    total_credits = sum(line['credits'] for line in st.session_state.journal_lines)
    st.metric(label="Total Debits", value=f"${total_debits:.2f}")
    st.metric(label="Total Credits", value=f"${total_credits:.2f}")

    # Statement Amount and Debit/Credit difference
    cols = st.columns([2, 2, 2])
    with cols[0]:
        st.metric(label="Statement Amount", value="$199.00")
    with cols[1]:
        st.metric(label="Journal Entry Lines", value=f"${total_debits:.2f}")
    with cols[2]:
        debit_short = 199.00 - total_debits
        st.metric(label="Debit amount short by", value=f"${debit_short:.2f}")

    if st.button('Clear Autofill'):
        st.session_state['journal_lines'] = [{'account': '', 'description': '', 'debits': 0.00, 'credits': 199.00}]
        st.experimental_rerun()

    if st.button('Save Journal Entry'):
        # Process the saved journal entry
        pass

invoice_df = None
journal_df = None

# Transaction input fields
if st.session_state.show_transaction:

    invoice_excel_uploader = st.file_uploader("Upload Invoice Excel File", type=['xlsx'], key='InvoiceExcel')
    journal_excel_uploader = st.file_uploader("Upload Journal Excel File", type=['xlsx'], key='JournalExcel')

    if invoice_excel_uploader is not None:
        invoice_df = pd.read_excel(invoice_excel_uploader)
    
    if journal_excel_uploader is not None:
        journal_df = pd.read_excel(journal_excel_uploader)

    invoice_button_label = None
    journal_button_label = None

    st.text_input('Amount', key='transaction_amount', value="50")
    st.text_input('Description', key='transaction_description', value="ATRO ATM/B2C ACCOUNT")
    st.text_input('Reference', key='transaction_reference', value="C94_452_200258 1111..0000 06/05/23 120604 88812510 1703")
    st.text_input('Payer/Payee', key='transaction_payer_payee', value="abc")

    if invoice_df is not None and journal_df is not None: 

        invoice_df = invoice_df.applymap(lambda x: str(x) if pd.notnull(x) else "")
        journal_df = journal_df.applymap(lambda x: str(x) if pd.notnull(x) else "")

        amount = st.session_state.get('transaction_amount', "")
        description = st.session_state.get('transaction_description', "")
        reference = st.session_state.get('transaction_reference', "")
        payer_payee = st.session_state.get('transaction_payer_payee', "")

        query_journal = ((journal_df['net_amount'] == amount) | (journal_df['net_amount'] == "") | (amount == "")) & \
                    ((journal_df['bse_description'] == description) | (journal_df['bse_description'] == "") | (description == "")) & \
                    ((journal_df['ext_reference'] == reference) | (journal_df['ext_reference'] == "") | (reference == "")) & \
                    ((journal_df['ext_contact_name'] == payer_payee) | (journal_df['ext_contact_name'] == "") | (payer_payee == ""))



        matched_rows_journal = journal_df.loc[query_journal]

        query_invoice = ((invoice_df['net_amount'] == amount) | (invoice_df['net_amount'] == "") | (amount == "")) & \
                    ((invoice_df['bse_description'] == description) | (invoice_df['bse_description'] == "") | (description == "")) & \
                    ((invoice_df['ext_reference'] == reference) | (invoice_df['ext_reference'] == "") | (reference == "")) & \
                    ((invoice_df['ext_contact_name'] == payer_payee) | (invoice_df['ext_contact_name'] == "") | (payer_payee == ""))
            

        matched_rows_invoice = invoice_df.loc[query_invoice]

        highlight_invoice = len(matched_rows_invoice) > len(matched_rows_journal)
        highlight_journal = not highlight_invoice  # Simplify to the opposite condition for clarity
        
        #################################################
        invoice_matches_count = len(matched_rows_invoice)
        journal_matches_count = len(matched_rows_journal)

        if invoice_matches_count > journal_matches_count:
            # Show the invoice form and autofill data
            st.session_state.show_transaction = False
            st.session_state.show_invoice_form = True
            autofill_invoice_data(invoice_df)
        elif journal_matches_count > invoice_matches_count:
            # Show the journal form and autofill data
            st.session_state.show_transaction = False
            st.session_state.show_journal_form = True
            autofill_journal_data(journal_df)
        else:
            # Handle the case where counts are equal or both are zero
            st.write("No clear match found. Please manually select the form to use.")
            
        #################################################

    #     invoice_button_label = "Invoice/Bill Receipt (Suggested)" if highlight_invoice else "Invoice/Bill Receipt"
    #     journal_button_label = "Journal Entry (Suggested)" if highlight_journal else "Journal Entry"

    #     if st.button(invoice_button_label):
    #         st.session_state.show_transaction = False
    #         st.session_state.show_invoice_form = True
    #         # show_invoice_form()
    #         start_time = datetime.now()
    #         autofill_invoice_data(invoice_df)
    #         end_time = datetime.now()
    #         time_diff = end_time - start_time
    #         st.write(f"Reconciliation process took {time_diff.total_seconds()} seconds.")

    #     if st.button(journal_button_label):
    #         st.session_state.show_transaction = False
    #         st.session_state.show_journal_form = True
    #         # display_journal_form()
    #         start_time = datetime.now()
    #         autofill_journal_data(journal_df)
    #         end_time = datetime.now()
    #         time_diff = end_time - start_time
    #         st.write(f"Reconciliation process took {time_diff.total_seconds()} seconds.")

    # else:

    #     if st.button("Invoice/Bill Receipt"):
    #         st.session_state.show_transaction = False
    #         st.session_state.show_invoice_form = True


    #         autofill_invoice_data(invoice_df)

    #     if st.button("Journal Entry"):
    #         st.session_state.show_transaction = False
    #         st.session_state.show_journal_form = True


    #         autofill_journal_data(journal_df)





if 'clear_form' not in st.session_state:
    st.session_state.clear_form = False

# Function to reset form values
def reset_form():
    st.session_state.clear_form = not st.session_state.clear_form  # Toggle the state to trigger the form reset


if st.session_state.show_invoice_form:
    st.session_state.show_transaction = False
    # Check if we need to clear the form (this needs to be at the start, before rendering widgets)
    if st.session_state.clear_form:
        # Reset all your session state variables here
        for key in ['InvoicepayMeth', 'tax_profile_name', 'tax_profile_tax_type_name', 'custom_fields', 'InvoiceContact', 'InvoiceDescript', 'invoiceaccount', 'tax_profile_vat_value']:
            st.session_state[key] = ''  # or your default value
        st.session_state.invoiceaccount = 'Select Account'
        st.session_state.vatinvoice = 'No VAT'
        # Toggle clear_form back to prevent continuous resetting
        st.session_state.clear_form = False
    

    # Your form widgets here
    st.text_input('Payment Method', key='InvoicepayMeth')
    st.text_input('tax_profile_name', key='tax_profile_name')
    st.text_input('tax_profile_tax_type_name', key='tax_profile_tax_type_name')
    st.text_input('custom_fields', key='custom_fields')
    st.text_input('Contact', key='InvoiceContact')
    st.text_input('Description', key='InvoiceDescript')
    st.text_input('invoiceaccount', key='invoiceaccount')
    st.text_input('tax_profile_vat_value', key='tax_profile_vat_value')
    st.file_uploader('Invoice Attachments', accept_multiple_files=True, key='invoiceAttachments')
    
    if st.button("Clear Autofill", on_click=reset_form):
        # The button now toggles the clear_form state, which is used to reset the form
        pass
    
    if st.button('Save Invoice', key='invoicesave'):
        # Process the saved invoice
        pass



if st.session_state.show_journal_form:
    if st.session_state.clear_form:
        
        for key in ['JounralReference', 'jorunalcontact', 'journalaccount', 'journaldescription', 'journalAmount', 'taxJournal']:
            st.session_state[key] = ''
        st.session_state.clear_form = False
    
    st.text_input('Journal Reference', value='Cash-in Transaction', key='JounralReference')
    st.text_input('Contact', key='jorunalcontact')
    st.text_input('Account', key='journalaccount')
    st.text_input('Description', key='journaldescription')
    st.text_input('Amount', key='journalAmount')
    st.text_input('Tax', key='taxJournal')

    if st.button("Clear Autofill", on_click=reset_form):
        # The button now toggles the clear_form state, which is used to reset the form
        pass
    
    if st.button('Save Journal', key='journalsave'):
        # Process the saved invoice
        pass
