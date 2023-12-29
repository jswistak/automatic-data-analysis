import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pdf2image import convert_from_bytes


# Streamlit UI
st.title("Automatic Tabular Data analysis")

# Define your options for the prompting technique here
prompting_techniques = ["Zero Shot"]
selected_technique = st.selectbox("Select Prompting Technique", prompting_techniques)

api_token = st.text_input("Enter API Token", type="password")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if st.button("Analyze"):
    if uploaded_file is not None and selected_technique and api_token:
        # data = pd.read_csv(uploaded_file)
        # pdf = create_pdf(data, selected_technique, api_token)
        # Here implement our function TODO

        st.success("Analysis Generated!")

        # Download button for the PDF
        st.download_button(
            label="Download PDF",
            # data=pdf,
            file_name="output.pdf",
            mime="application/octet-stream",
        )

        # Convert PDF to images and display
        images = convert_from_bytes(pdf.getvalue())
        for image in images:
            st.image(image, use_column_width=True)

    else:
        st.error("Please fill in all fields and upload a CSV file.")
