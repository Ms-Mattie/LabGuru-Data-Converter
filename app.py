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
    df = pd.read_csv(uploaded_file, encoding='utf-8-sig')  # Using utf-8-sig for better compatibility

    # Display the uploaded data at the top
    st.write("Uploaded Data:")
    st.dataframe(df)

    # Add 'Stock ID' column (blank for LIMS upload)
    df['Stock ID'] = ""

    # Apply transformations across all rows explicitly
    df['Stock name *'] = df['Label']  # Stock name = Label

    df['Privacy'] = "Public"  # Privacy = Public

    df['Stock type'] = "Tube"  # Stock type = Tube

    df['Stock color'] = "gray"  # Stock color = gray

    # Concatenate 'Diagnosis', 'Histology', and 'Pathologic_Stage' for **every row**
    # Fill NaN values with an empty string to avoid issues with concatenation
    df['Stock description'] = df['Diagnosis'].fillna('') + " " + df['Histology'].fillna('') + " " + df['Pathologic_Stage'].fillna('')

    df['Stock concentration'] = stock_concentration  # User input for stock concentration

    df['Concentration units'] = concentration_units  # User input for concentration units

    df['Concentration remarks'] = concentration_remarks  # User input for concentration remarks

    df['Stock volume'] = df['Approx. Volume (uL)']  # Stock volume = Approx. Volume (uL)

    df['Volume units'] = volume_units  # Volume units = user input

    df['Volume remarks'] = st.text_input("Volume Remarks (if applicable)")  # User input for volume remarks

    # Set the blank values for Stock weight, Weight units, and Weight remarks
    df['Stock weight'] = ""
    df['Weight units'] = ""
    df['Weight remarks'] = ""

    df['Stock units'] = stock_units  # User input for stock units

    df['Stock count'] = "1"  # Stock count = 1

    df['Stock lot'] = st.text_input("Stock Lot (if applicable)")  # User input for stock lot

    # Set the blank values for Stock barcode, expiry date, and created at
    df['Stock barcode'] = ""
    df['Stock expiry date'] = ""
    df['Stock owner'] = stock_owner  # User input for Stock Owner
    df['Stored / Frozen By'] = stored_frozen_by  # User input for Stored / Frozen By
    df['Stored / Frozen On'] = stored_frozen_on  # User input for Stored / Frozen On
    df['Created at'] = ""

    df['Box name'] = df['Box Label']  # Box name = Box Label

    # Box dimensions and location will remain blank
    df['Box dimensions - # rows'] = ""
    df['Box dimensions - # columns'] = ""
    df['Box location in Rack - Cells'] = ""

    # Stock position: incrementing from 1 to 81 for each row
    df['Stock position'] = range(1, len(df) + 1)

    # Leave storage location and other fields blank as required
    df['Storage location'] = ""
    df['Inventory collection *'] = inventory_collection
    df['Inventory item name'] = inventory_item_name
    df['Inventory item sysID'] = ""

    # **Column Filtering**: Ensure all LIMS-required columns are included, even if empty
    output_columns = [
        'Stock ID', 'Stock name *', 'Privacy', 'Stock type', 'Stock color', 
        'Stock description', 'Stock concentration', 'Concentration units', 
        'Concentration remarks', 'Stock volume', 'Volume units', 'Volume remarks', 
        'Stock weight', 'Weight units', 'Weight remarks', 'Stock units', 
        'Stock count', 'Stock lot', 'Stock barcode', 'Stock expiry date',
	'Stock owner', 'Stored / Frozen By', 'Stored / Frozen On',
        'Created at', 'Box name', 'Box dimensions - # rows', 'Box dimensions - # columns', 
        'Box location in Rack - Cells', 'Stock position', 'Storage location', 
        'Inventory collection *', 'Inventory item name', 'Inventory item sysID'
    ]

    # Ensure the column order is correct, and remove any additional columns
    df_output = df[output_columns]

    # **Fix Encoding Issues**: Explicitly replace any invalid volume units (like ÅµL or ÂµL)
    # Now we replace both ÅµL and any malformed unit
    df_output['Volume units'] = df_output['Volume units'].apply(lambda x: re.sub(r'[^\x00-\x7F]+', 'µL', str(x)) if isinstance(x, str) else x)
    
    # Ensure there's only one "L" at the end of "µL"
    df_output['Volume units'] = df_output['Volume units'].str.replace('µLL', 'µL', regex=False)

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
