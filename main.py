from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit as st
import fitz  # PyMuPDF

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("GITHUB_TOKEN")
)

# Streamlit app title
st.title("ChatGPT-like clone")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
with st.container():
    st.subheader("Chat History")
    if not st.session_state.messages:
        st.info("No messages yet. Start the conversation!")
    else:
        for message in st.session_state.messages:
            with st.expander(f"{message['role'].capitalize()} says:"):
                st.markdown(message["content"])

# File uploader for users to upload files
uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf"])

# Variable to store the extracted file content
file_content = ""

if uploaded_file:
    if uploaded_file.type not in ["text/plain", "application/pdf"]:
        st.warning(f"Unsupported file type: {uploaded_file.type}. Only .txt and .pdf files are supported.")
    else:
        file_contents = uploaded_file.read()

        # Process text files
        if uploaded_file.type == "text/plain":
            file_content = file_contents.decode("utf-8")
        
        # Process PDF files
        elif uploaded_file.type == "application/pdf":
            pdf_document = fitz.open(stream=file_contents, filetype="pdf")
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            file_content = text

# Chat functionality
if prompt := st.chat_input("What is up?"):
    modified_prompt = 'All answers please provide only in Lithuania language'

    # Append the user input to the session messages
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare the messages for the OpenAI API
    messages_for_api = [{"role": "system", "content": modified_prompt}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]
    
    # Optionally add file contents to the conversation context (if there's an uploaded file)
    if uploaded_file and file_content:
        messages_for_api.append({"role": "system", "content": f"The uploaded file contains the following content: {file_content[:1000]}..."})  # Adding first 1000 chars for brevity

    # Get assistant response using the OpenAI client
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gpt-4o",  # Use the correct model name here
            messages=messages_for_api,
        ).choices[0].message.content
        
        st.markdown(response)

    # Add assistant's response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})