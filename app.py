import os
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pdf2image import convert_from_bytes
from main import main, get_runtime_kwargs
from dotenv import load_dotenv


load_dotenv()
DATA_PATH = ""
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

        try:
            with open(os.path.join(DATA_PATH, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
                dataset_path = os.path.join(DATA_PATH, uploaded_file.name)
                runtime = "jupyter-notebook"
                analysis_assistant = "openai"
                code_assistant = "openai"
                prompt_name = "zero-shot"
                kwargs = get_runtime_kwargs(runtime, code_assistant, analysis_assistant)
                # kwargs["analysis_assistant"]["api_key"] = assistant_api_key
                # kwargs["code_assistant_kwargs"]["api_key"] = assistant_api_key
                print(kwargs)
                print("\n")

                output_pdf_path = main(
                    dataset_path,
                    runtime,
                    code_assistant,
                    analysis_assistant,
                    prompt_name,
                    **kwargs,
                )

                # TODO open ai api key; steps of analysis (api calls)

                st.success("Analysis Generated!")

                if os.path.exists(output_pdf_path):
                    with open(output_pdf_path, "rb") as file:
                        btn = st.download_button(
                            label="Download PDF",
                            data=file,
                            file_name="downloaded_file.pdf",
                            mime="application/octet-stream",
                        )
                        images = convert_from_bytes(file.getvalue())
                        for image in images:
                            st.image(image, use_column_width=True)
                else:
                    st.write("Output file not found.")

        # except Exception as e:
        #     print(e)
        #     st.error("Something went wrong!")

        finally:
            os.remove(os.path.join(DATA_PATH, uploaded_file.name))

    else:
        st.error("Please fill in all fields and upload a CSV file.")
