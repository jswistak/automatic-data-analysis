from datetime import datetime
import os
import streamlit as st
import pandas as pd
from tempfile import NamedTemporaryFile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pdf2image import convert_from_bytes
from main import main, get_runtime_kwargs
from dotenv import load_dotenv
import traceback


load_dotenv()
# Streamlit UI
st.title("Automated Tabular Data analysis")

# Define your options for the prompting technique here
prompting_techniques = {"Zero Shot": "zero-shot"}

prompting_technique = st.selectbox(
    "Select Prompting Technique", prompting_techniques.keys()
)
code_assistants = {"OpenAI": "openai", "LLaMA2 Chat": "llama-chat"}
code_assistant = st.selectbox("Select Code Assistant", code_assistants.keys())

analysis_assistants = {"OpenAI": "openai", "LLaMA2 Chat": "llama-chat"}
analysis_assistant = st.selectbox(
    "Select Analysis Assistant", analysis_assistants.keys()
)

if code_assistant == "OpenAI" or analysis_assistant == "OpenAI":
    llm_token = st.text_input("Enter API Token", type="password")
else:
    llm_token = None

analysis_message_limit = st.number_input(
    "Analysis Message Limit", min_value=3, max_value=40, value=3
)

uploaded_file = st.file_uploader("Upload CSV", type="csv")

# TODO: Add a button to select the runtime

if (
    uploaded_file
    and code_assistant
    and analysis_assistant
    and prompting_technique
    and analysis_message_limit
    and (llm_token or (code_assistant != "OpenAI" and analysis_assistant != "OpenAI"))
    and st.button("Analyze")
):
    try:
        # TODO: Save the uploaded file to a temporary location

        with NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.read())
            dataset_name = uploaded_file.name
            dataset_path = tmp.name

            runtime = "jupyter-notebook"

            kwargs = get_runtime_kwargs(
                runtime,
                code_assistants[code_assistant],
                analysis_assistants[analysis_assistant],
            )
            if llm_token:
                kwargs["analysis_assistant_kwargs"]["api_key"] = llm_token
                kwargs["code_assistant_kwargs"]["api_key"] = llm_token
            output_pdf_path = main(
                dataset_name,
                dataset_path,
                runtime,
                code_assistants[code_assistant],
                analysis_assistants[analysis_assistant],
                prompting_techniques[prompting_technique],
                analysis_message_limit=analysis_message_limit,
                **kwargs,
            )

            # TODO open ai api key; steps of analysis (api calls)

            st.success("Analysis Generated!")

            if os.path.exists(output_pdf_path):
                with open(output_pdf_path, "rb") as file:
                    file_content = file.read()
                    btn = st.download_button(
                        label="Download PDF",
                        data=file_content,
                        file_name=f"downloaded_file{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.pdf",
                        mime="application/octet-stream",
                    )
                    images = convert_from_bytes(file_content)
                    for image in images:
                        st.image(image, use_column_width=True)
            else:
                st.write("Output file not found.")

    except Exception as e:
        st.error("An error occurred while analyzing the data: " + str(e))
        traceback.print_exc()

    finally:
        # TODO temporarily save the input file
        pass
        # os.remove(os.path.join(DATA_PATH, uploaded_file.name))
