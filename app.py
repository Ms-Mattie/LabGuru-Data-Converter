import streamlit as st
import pandas as pd
import re

# Set the title
st.title("LabGuru Data Converter")

# Add instructions under the title
st.markdown("""
    **This app converts data from the MASTER_Freezer Inventory Excel document into the correct format for the LabGuru Stock Upload template.**

    **To use the tool:**

    - Complete the fields below, which will be included in the LabGuru upload.
    - For clarity on the fields, hover your mouse over the question mark to the right of the entry field for additional information. 
    - The box name and sample position in the LabGuru template will match the corresponding entry in the MASTER_Freezer Inventory.
    - For uploading to LabGuru, copy/paste the transformed rows onto a newly downloaded Stock Upload Template. 
    - For issues or questions, please contact Mattie at mattie.goldberg@aoadx.com.
""")

# File upload widget
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

# User input fields for manual transformations with additional descriptions
stock_concentration = st.text_input("Stock Concentration (if applicable)", help="This is the concentration of the solution. If this is serum, leave this field blank.")
concentration_units = st.text_input("Concentration Units (if applicable)", help="This refers to the concentration units of the solution. If this is serum, leave this field blank.")
concentration_remarks = st.text_input("Concentration Remarks (if applicable)", help="If the sample was prepared in the lab, note who prepared it and based on what procedure.")
volume_units = st.selectbox("Volume Units", ["L", "mL", "µL", "Strips", "column"], help="Please, notate the units of volume in the sample.")
stock_units = st.text_input("Stock Units", help="If you would like duplicates of the same row to be generated under identical names (for example, this is the name of many aliquots), assign the number of aliquots you'd like to be generated in LabGuru in this field.")
inventory_collection = st.text_input("Inventory Collection", help="This is based on the LabGuru file structure. For example, if this is a serum sample, then this field must be 'Serum'.")
inventory_item_name = st.text_input("Inventory Item Name", help="This is the name of the sample item based on the LabGuru file structure. Stocks represent the individual samples underneath the umbrella of an Item. For example, the item is 'Skywalker' and the stocks are the individual samples like 'SW_001'. If this Item does not already exist, please, add it to LabGuru before uploading this transformed document.")
stock_owner = st.text_input("Stock Owner", help="This is the person responsible for the sample. Write their full name as it is described as their LabGuru member.")
stored_frozen_by = st.text_input("Stored / Frozen By", help="This is the person who prepared the sample. Write their full name as it is described as their LabGuru member.")
stored_frozen_on = st.text_input("Stored / Frozen On", help="This is the date the sample was prepared. Use format YYYY-MM-DD.")

if uploaded_file is not None:
    # Read the CSV file into a pandas dataframe with utf-8-sig encoding
    df = pd.read_csv(uploaded_file, encoding='utf-8-sig')

    # Add 'Stock ID' column (blank for LIMS upload)
    df['Stock ID'] = ""

    # Apply transformations across all rows explicitly using correct column mappings
    df['Stock name *'] = df['Label']  # Map Label to Stock name *
    df['Stock owner'] = stock_owner  # Map Stock owner from app input
    df['Stored / frozen on'] = stored_frozen_on  # Use Stored_frozen_on input from the app
    df['Stored / frozen by'] = stored_frozen_by  # Use Stored_frozen_by input from the app
    df['Stock position'] = df['Position']  # Map Position to Stock position
    df['Inventory collection *'] = inventory_collection  # Map Inventory Collection to Inventory collection *
    df['Inventory item name'] = inventory_item_name  # Map Inventory item name to Inventory item name
    df['Box name'] = df['Box Label']  # Map Box Label to Box name
    df['Stock volume'] = df['Approx. Volume (uL)']  # Map Approx. Volume (uL) to Stock volume

    # Set the blank values for Weight units, Weight remarks, and others as needed
    df['Stock weight'] = ""
    df['Weight units'] = ""
    df['Weight remarks'] = ""

    # Additional columns (blank values)
    df['Stock count'] = "1"  # Stock count = 1
    df['Stock lot'] = st.text_input("Stock Lot (if applicable)")  # User input for stock lot
    df['Stock barcode'] = ""
    df['Stock expiry date'] = ""
    df['Created at'] = ""

    # Ensure that the output includes the right columns for LabGuru
    output_columns = [
        'Stock ID', 'Stock name *', 'Privacy', 'Stock type', 'Stock color',
        'Stock description', 'Stock concentration', 'Concentration units',
        'Concentration remarks', 'Stock volume', 'Volume units', 'Volume remarks',
        'Stock weight', 'Weight units', 'Weight remarks', 'Stock units',
        'Stock count', 'Stock lot', 'Stock barcode', 'Stock expiry date',
        'Created at', 'Box name', 'Box dimensions - # rows', 'Box dimensions - # columns',
        'Box location in Rack - Cells', 'Stock position', 'Storage location',
        'Inventory collection *', 'Inventory item name', 'Inventory item sysID'
    ]

    # Ensure that the columns are in the correct order
    df_output = df[output_columns]

    # Display the transformed and filtered data
    st.write("Transformed Data:")
    st.dataframe(df_output)

    # Provide download option for the transformed file with UTF-8 BOM encoding (helps Excel)
    csv = df_output.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

    st.download_button(
        label="Download Transformed CSV",
        data=csv,
        file_name="transformed_data.csv",
        mime="text/csv"
    )
