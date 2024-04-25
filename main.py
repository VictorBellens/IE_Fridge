import streamlit as st
import pandas as pd
import os

from ocr import processed_text, parse_response


FRIDGE_CSV = "fridge_inventory.csv"


def load_fridge_inventory():
    if os.path.exists(FRIDGE_CSV):
        try:
            return pd.read_csv(FRIDGE_CSV)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=['Item', 'Quantity', 'Expiration Date'])
    else:
        return pd.DataFrame(columns=['Item', 'Quantity', 'Expiration Date'])


def write_to_csv(parsed_entries, filename=FRIDGE_CSV):
    df = pd.DataFrame(parsed_entries)
    df.to_csv(filename, index=False)


fridge_inventory = load_fridge_inventory()


if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Upload'


def set_page(page):
    st.session_state['current_page'] = page


col1, col2 = st.columns([1, 1])

with col1:
    st.button('Upload', on_click=set_page, args=('Upload',))
with col2:
    st.button('Fridge', on_click=set_page, args=('Fridge',))

current_page = st.session_state['current_page']

if current_page == 'Upload':
    st.header('Upload your receipt')
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        st.write("File uploaded successfully.")
        with open(os.path.join("previous_receipts", uploaded_file.name), 'wb') as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Analyzing..."):
            receipt_info = processed_text(os.path.join(f"previous_receipts/{uploaded_file.name}"))
        if receipt_info is not None:
            parsed_info = parse_response(receipt_info)
            write_to_csv(parsed_info)
            st.write("File analyzed successfully.")
        else:
            st.write("There was an error with the analysis.")


elif current_page == 'Fridge':
    st.header('Items in your fridge')

    fridge_inventory = load_fridge_inventory()

    if not fridge_inventory.empty:
        primer = True
        for index, row in fridge_inventory.iterrows():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if primer:
                    st.text("ITEM")
                st.text(row['item'])
            with col2:
                if primer:
                    st.text("QUANTITY")
                st.text(f"{row['quantities']}")
            with col3:
                if primer:
                    st.text("EXPIRATION")
                    primer = False
                st.text(f"{row['expiration date']}")
            with col4:
                if st.button('Remove', key=f'remove_{index}'):
                    # If the quantity after removal is 0, remove the item from the DataFrame
                    if row['quantities'] > 1:
                        fridge_inventory.at[index, 'quantities'] -= 1
                    else:
                        fridge_inventory = fridge_inventory.drop(index)
                    write_to_csv(fridge_inventory, FRIDGE_CSV)
                    fridge_inventory = load_fridge_inventory()
                    st.experimental_rerun()
    else:
        st.write("Your fridge is empty!")
