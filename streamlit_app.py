#Imports
import os
import uuid
import streamlit as st
import requests
from prompt import SYSTEM_PROMPT
from document_db import load_documents
from urllib.parse import quote

st.set_page_config(
    page_title="SchedulePilot-AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 SchedulePilot-AI")

if "active_namespace" not in st.session_state:
    st.session_state.active_namespace = None

# ==========================
# Thread ID
# ==========================

if "thread_id" not in st.session_state:

    st.session_state.thread_id = str(
        uuid.uuid4()
    )

if "uploaded_pdfs" not in st.session_state:

    response = requests.get(
        "http://127.0.0.1:8000/pdfs"
    )

    st.session_state.uploaded_pdfs = (
        response.json()
    )

if "selected_pdf" not in st.session_state:
    st.session_state.selected_pdf = None

with st.sidebar:

    st.header(
        "📚 PDFs"
    )

    # ==========================
    # New Chat
    # ==========================

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        # Create new conversation thread
        st.session_state.thread_id = str(
            uuid.uuid4()
        )

        # Clear chat messages
        st.session_state.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        # Remove selected PDF
        st.session_state.active_namespace = None

        st.session_state.selected_pdf = None

        st.rerun()

    for pdf_name in list(
        st.session_state.uploaded_pdfs.keys()
    ):

        col1, col2 = st.columns(
            [3,1]
        )

        with col1:
            button_label = pdf_name

            if pdf_name == st.session_state.selected_pdf:
                button_label = f"✅ {pdf_name}"

            if st.button(
                button_label,
                key=f"select_{pdf_name}"
            ):

                st.session_state.active_namespace = (
                    st.session_state.uploaded_pdfs[
                        pdf_name
                    ]
                )
                st.session_state.selected_pdf = pdf_name

        with col2:

            if st.button(
                "🗑️",
                key=f"delete_{pdf_name}"
            ):
                response = requests.delete(
                    f"http://127.0.0.1:8000/delete-pdf/{quote(pdf_name)}"
                )

                if response.status_code == 200:

                    del st.session_state.uploaded_pdfs[
                        pdf_name
                    ]

                    st.rerun()


st.markdown("---")

# ==========================
# PDF Upload Section
# ==========================

st.subheader("📄 Upload PDF")
#file upload
uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)

if uploaded_file:
    #Creates a data folder
    os.makedirs(
        "data",
        exist_ok=True
    )
    #Creates a file path
    file_path = os.path.join(
        "data",
        uploaded_file.name
    )
    #saves the uploaded file to the data folder
    with open(file_path, "wb") as f:
        f.write(
            uploaded_file.getbuffer()
        )

    st.success(
        f"{uploaded_file.name} uploaded successfully."
    )

    if st.button("🚀 Process PDF"):

        with st.spinner(
            "Uploading PDF to Pinecone..."
        ):
            #uploads the PDF to Pinecone 
            with open(file_path, "rb") as pdf_file:

                response = requests.post(
                    "http://127.0.0.1:8000/upload-pdf",
                    files={
                        "file": pdf_file
                    }
                )

            if response.status_code != 200:

                st.error(
                    f"Upload failed.\n\n{response.text}"
                )

                st.stop()
            result = response.json()

            if "error" in result:

                st.error(
                    result["error"]
                )

                st.stop()

            st.session_state.uploaded_pdfs[
                uploaded_file.name
            ] = result["namespace"]

            st.session_state.active_namespace = (
                result["namespace"]
            )
            st.session_state.selected_pdf = uploaded_file.name


        st.success(
            f"""
            PDF processed successfully.

            Namespace:
            {result['namespace']}

            Chunks:
            {result['chunks']}
            """
        )

st.markdown("---")

# ==========================
# CHAT SECTION
# ==========================

st.subheader("💬 Chat")

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


# Display Previous Messages

for msg in st.session_state.messages:

    if msg["role"] == "system":
        continue

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# Chat Input

user_input = st.chat_input(
    "Ask anything..."
)

if user_input:

    # Show User Message

    with st.chat_message("user"):
        st.markdown(user_input)

    # Save User Message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Generate Answer
    
    with st.chat_message("assistant"):
            
        with st.spinner("Thinking..."):

            if st.session_state.active_namespace is None:

                st.warning(
                    "Please upload a PDF first."
                )

                st.stop()
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                json={
                    "question": user_input,
                    "namespace": st.session_state.active_namespace,
                    "thread_id": st.session_state.thread_id
                }
            )

            if response.status_code != 200:

                st.error(
                    response.text
                )

                st.stop()

            answer = response.json()["answer"]

            st.markdown(answer)

    # Save Message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )