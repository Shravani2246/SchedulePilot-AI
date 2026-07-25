import os  # Import OS module for file system operations
import asyncio
import uuid

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    WebSocket,
    WebSocketDisconnect
)
from services.deepgram_service import (
    DeepgramService
)

from backend.schemas import ChatRequest

from document_db import (
    load_documents,
    delete_document,
    get_namespace
)

from delete_pdf import (
    delete_namespace
)
import agent
from services.runtime_context import (
    set_current_thread_id
)



from pdf_ingest import upload_pdf_to_pinecone  # Import function to process and store PDF in Pinecone

app = FastAPI()  # Create FastAPI app instance

deepgram = DeepgramService()

@app.get("/")  # Root endpoint
def home():  # Home route function

    return {
        "message": "RAG Backend Running"  # Simple API status message
    }

@app.get("/pdfs")
def get_pdfs():

    return load_documents()

@app.post("/upload-pdf")  # Endpoint to upload PDF file
async def upload_pdf(  # Async function to handle file upload
    file: UploadFile = File(...)  # Receive file from request
):

    os.makedirs(  # Create directory if it doesn't exist
        "data",  # Folder name for storing uploaded PDFs
        exist_ok=True  # Prevent error if folder already exists
    )

    file_path = os.path.join(  # Construct full file path
        "data",  # Target directory
        file.filename  # Original uploaded file name
    )

    with open(  # Open file in write-binary mode
        file_path,  # Path where file will be saved
        "wb"  # Write binary mode for PDF files
    ) as f:

        f.write(  # Write uploaded file content to disk
            await file.read()  # Read uploaded file asynchronously
        )

    try:

        result = upload_pdf_to_pinecone(
            file_path
        )

        return result

    except Exception as e:

        return {
            "error": str(e)
        }

@app.delete("/delete-pdf/{filename}")
def remove_pdf(filename: str):

    namespace = get_namespace(
        filename
    )

    if namespace:

        delete_namespace(
            namespace
        )

        delete_document(
            filename
        )

    return {
        "message":
        "PDF deleted successfully"
    }

@app.post("/chat")
def chat(request: ChatRequest):

    print(
        "\nCHAT REQUEST NAMESPACE:",
        request.namespace
    )

    print(
        "THREAD ID:",
        request.thread_id
    )

    agent.ACTIVE_NAMESPACE = (
        request.namespace
    )

    set_current_thread_id(
        request.thread_id
    )

    response = agent.agent.invoke(
        {
            "messages": [
                (
                    "user",
                    request.question
                )
            ]
        },
        config={
            "configurable": {
                "thread_id": request.thread_id
            }
        }
    )

    answer = response[
        "messages"
    ][-1].content

    return {
        "answer": answer
    }

def read_audio_file(
    audio_file: str
) -> bytes:

    with open(
        audio_file,
        "rb"
    ) as file:

        return file.read()
    
# ==========================
# Voice WebSocket
# ==========================

@app.websocket("/voice")
async def voice_socket(
    websocket: WebSocket
):

    await websocket.accept()
    voice_thread_id = str(
        uuid.uuid4()
    )

    print(
        "\nVOICE CLIENT CONNECTED"
    )

    try:

        while True:

            user_message = await websocket.receive_text()

            print(
                "VOICE MESSAGE:",
                user_message
            )

            agent.ACTIVE_NAMESPACE = None

            set_current_thread_id(
                voice_thread_id
            )

            # --------------------------
            # Run Agent
            # --------------------------

            try:

                response = await asyncio.to_thread(
                    agent.agent.invoke,
                    {
                        "messages": [
                            (
                                "user",
                                user_message
                            )
                        ]
                    },
                    config={
                        "configurable": {
                            "thread_id": voice_thread_id
                        }
                    }
                )
            except Exception:

                import traceback

                traceback.print_exc()

                await websocket.send_text(
                    "Agent crashed"
                )

                continue

            answer = response[
                "messages"
            ][-1].content

            print(
                "AGENT FINISHED"
            )

            # --------------------------
            # Text To Speech
            # --------------------------

            try:

                audio_file = await asyncio.to_thread(
                    deepgram.text_to_speech,
                    answer
                )

                print(
                    "TTS FINISHED"
                )

            except Exception:

                import traceback

                traceback.print_exc()

                await websocket.send_text(
                    "TTS Error"
                )

                continue

            # --------------------------
            # Read Audio File
            # --------------------------

            try:

                audio_bytes = await asyncio.to_thread(
                    read_audio_file,
                    audio_file
                )

            except Exception:

                import traceback

                traceback.print_exc()

                await websocket.send_text(
                    "Audio read error"
                )

                continue

            # --------------------------
            # Send Audio
            # --------------------------

            await websocket.send_bytes(
                audio_bytes
            )

            print(
                "AUDIO SENT"
            )


            # --------------------------
            # Delete Temporary Audio
            # --------------------------

            try:

                if os.path.exists(
                    audio_file
                ):

                    os.remove(
                        audio_file
                    )

                    print(
                        "TEMP AUDIO DELETED"
                    )

            except OSError as e:

                print(
                    "TEMP AUDIO DELETE ERROR:",
                    str(e)
                )

    except WebSocketDisconnect:

        print(
            "VOICE CLIENT DISCONNECTED"
        )

    except Exception:

        import traceback

        print(
            "\nVOICE ERROR"
        )

        traceback.print_exc()