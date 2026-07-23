# SchedulePilot-AI — Project Documentation

This document describes the codebase structure, architecture, workflows, modules, services, database interactions, external APIs, environment variables, and dependencies — derived directly from the repository source files. No functionality is invented; all statements are based on the code.

---

## 1. Project Overview

SchedulePilot-AI is an assistant that: 1) answers questions about uploaded PDF documents via a Pinecone-backed RAG flow; and 2) schedules meetings using Google Calendar and sends confirmation emails via Gmail. The repository contains a Streamlit-based UI, a FastAPI backend, PDF ingestion and retrieval logic, an AI agent (LangGraph + Azure OpenAI), calendar/email tooling, and Postgres-based document registry storage.

---

## 2. Top-level files and purpose

- `streamlit_app.py` — Streamlit frontend UI. Uploads PDFs, lists uploaded PDFs, and sends chat requests to the backend at `POST /chat`. Shows chat messages in the browser.
- `backend/main.py` — FastAPI app that exposes endpoints used by the frontend:
  - `GET /` (status message)
  - `GET /pdfs` → returns `document_db.load_documents()` mapping
  - `POST /upload-pdf` → saves uploaded file to `data/` and calls `upload_pdf_to_pinecone()`
  - `DELETE /delete-pdf/{filename}` → deletes the Pinecone namespace and document registry entry
  - `POST /chat` → receives `{question, namespace}` and calls the agent via `agent.agent.invoke(...)`
- `app.py` — simple CLI loop that interacts directly with `agent` (agent.invoke) for manual testing.
- `agent.py` — configures the LLM and tools, and builds the LangGraph react-style agent (uses `create_react_agent`). Tools registered include `pdf_search`, `current_time`, `multiply`, and `create_calendar_event`.
- `prompt.py` — the system prompt used by the LLM. It instructs the model when to use `pdf_search` vs `create_calendar_event`, and how to collect/normalize scheduling information.
- `PROJECT_DOCUMENTATION.md` — (this file) project documentation generated from source.

---

## 3. Services and helper modules

- `services/google_auth.py`
  - Handles Google OAuth flow and token persistence.
  - SCOPES set to calendar and Gmail send: `https://www.googleapis.com/auth/calendar` and `https://www.googleapis.com/auth/gmail.send`.
  - Reads `credentials.json` and writes `token.json`.
  - Returns `google.oauth2.credentials.Credentials` used by Calendar and Gmail clients.

- `services/google_calendar.py`
  - Wraps Google Calendar API (`googleapiclient.discovery.build("calendar","v3")`).
  - Methods:
    - `create_event(title, start_datetime, duration_minutes=60, description="", location="")` — localizes to `Asia/Kolkata`, builds start/end payload, inserts event in `primary` calendar and returns the created event object.
    - `check_availability(start_datetime, duration_minutes)` — lists events in the time range and returns `True` if no overlapping items.

- `services/gmail_service.py`
  - Wraps Gmail API (`googleapiclient.discovery.build("gmail","v1")`).
  - Method `send_email(to, subject, body)` — constructs a MIMEText message, base64-encodes it, and sends with `users().messages().send(userId="me", body=...)`.
  - Uses `authenticate_google()` for credentials.

- `tools/calendar_tool.py`
  - A LangChain/agent tool decorated with `@tool` named `create_calendar_event(title, date, time, duration_minutes)`.
  - Responsibilities:
    - Validate `date` format `YYYY-MM-DD` and `time` format `HH:MM` (24-hour).
    - Validate `duration_minutes` > 0.
    - Combine date+time into a `datetime` and call `calendar_service.check_availability(...)`.
    - If available, create event with `calendar_service.create_event(...)` and then send a confirmation email using `gmail_service.send_email(...)`.
    - Returns a human-readable message with `event['htmlLink']` on success or an error string.
  - Important: the confirmation `to` address is hardcoded to `shravanisonawane22@gmail.com` in the code.

---

## 4. RAG / PDF ingestion and retrieval

- `pdf_ingest.py` — ingests a PDF file into Pinecone:
  - Loads PDF via `PyPDFLoader` (from `langchain_community.document_loaders`).
  - Splits pages into chunks with `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)`.
  - Uses `pinecone.Pinecone` client to connect to the index at `PINECONE_HOST` and upserts records in a namespace derived from filename (lowercased, ` .pdf` removed, spaces → `_`).
  - After successful upsert, calls `document_db.add_document(filename, namespace)` to persist the filename→namespace mapping in the Postgres-backed registry.

- `rag.py` — search helper:
  - Creates a `Pinecone` client and `Index(host=PINECONE_HOST)` at import time.
  - Function `search_pdf(query, namespace)` executes an index search (top_k=5) and returns concatenated text chunks (with page metadata) from the hits.

---

## 5. Database and registry

- `database.py` — supplies `get_connection()` which opens a `psycopg2` connection using environment variables for a Postgres/Supabase instance.

- `document_db.py` — a thin Postgres-backed document registry:
  - `add_document(filename, namespace)` — inserts the mapping into `documents (filename, namespace)` with `ON CONFLICT(filename) DO NOTHING`.
  - `load_documents()` — returns a `{filename: namespace}` dictionary of all rows.
  - `get_namespace(filename)` — returns namespace for a given filename.
  - `document_exists(filename)` — checks for existence (by `id` select).
  - `delete_document(filename)` — delete row by filename.

- `test.py` — a small script that attempts to connect to the Postgres host configured in environment variables and prints connection status (used to verify DB connectivity).

Note: SQL schema is not in the repository; `document_db` expects a `documents` table with at least `filename`, `namespace`, and `id` columns (inferred from queries). Schema creation is not present in code.

---

## 6. External APIs and services used

- Pinecone (via `pinecone.Pinecone`) — vector index for storing PDF chunks and searching.
- Google Calendar API — to create events and check availability.
- Gmail API — to send confirmation emails.
- Google OAuth (`google-auth`, `google-auth-oauthlib`) — interactive auth flow; `credentials.json` and `token.json` used.
- Azure OpenAI (via `langchain_openai.AzureChatOpenAI`) — LLM model used by the agent.

All API usage is driven from the code in `services/*`, `tools/calendar_tool.py`, `pdf_ingest.py`, `rag.py`, and `agent.py`.

---

## 7. Environment variables (from `config.py`)

The code reads the following environment variables (via `python-dotenv`):

- `OPENAI_API_KEY` — optional / not used in `agent.py` (the code uses Azure vars), present in `config.py`.
- `OPENAI_MODEL` — default `gpt-4o-mini` if not set.

Azure OpenAI config (used by `agent.py`):
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_DEPLOYMENT_NAME`

Pinecone config (used by `pdf_ingest.py`, `rag.py`, `upload_pdf.py`):
- `PINECONE_API_KEY`
- `PINECONE_HOST`
- `PINECONE_NAMESPACE` (present in `config.py`, not used everywhere; some scripts expect `NAMESPACE` or `PINECONE_NAMESPACE` — see individual files)

Postgres / Supabase config (used by `database.py` / `document_db.py`):
- `SUPABASE_DB_HOST`
- `SUPABASE_DB_NAME`
- `SUPABASE_DB_USER`
- `SUPABASE_DB_PASSWORD`
- `SUPABASE_DB_PORT`

Other environment keys referenced in some scripts (present but may not be used everywhere):
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` (referenced in `upload_pdf.py`)
- `NAMESPACE` and `PINECONE_INDEX_NAME` (referenced in `upload_pdf.py`) — these appear in `upload_pdf.py` but are not defined or used consistently across the codebase.

Files `credentials.json` and `token.json` are used by `services/google_auth.py` for Google OAuth; `credentials.json` is present in the repository.

---

## 8. Dependencies (from `requirements.txt`)

The project lists these packages (as found in `requirements.txt`):

- openai
- python-dotenv
- streamlit
- langchain-openai
- langgraph
- langchain
- langgraph-checkpoint
- pinecone
- langchain-pinecone
- pypdf
- langchain-community
- langchain-text-splitters
- requests
- fastapi
- torchvision
- psycopg2-binary

Note: The current `requirements.txt` contains duplicates and some spacing — use it as a starting point for installation. Some packages (e.g., `torchvision`) may bring heavy native dependencies.

---

## 9. Agent, tools and LLM integration

- `agent.py` constructs the LLM client using `AzureChatOpenAI` with Azure environment variables from `config.py`.
- It registers tools with `@tool` (LangChain-style) so the model can call them. Tools defined:
  - `multiply(a,b)` — simple example tool
  - `current_time()` — returns now (used by prompt for relative date resolution)
  - `pdf_search(question)` — uses `rag.search_pdf` to search the active Pinecone namespace
  - `create_calendar_event` — imported from `tools/calendar_tool.py`
- The system prompt (`prompt.py`) instructs the model to:
  - use `pdf_search` for PDF questions
  - use `create_calendar_event` for meeting scheduling, but only after collecting `title`, `date`, `time`, `duration_minutes`
  - normalize natural-language relative dates/times and request `current_time()` if needed to resolve relative dates

---

## 10. Scheduling workflow (data flow for meeting scheduling)

1. User types a scheduling request into `streamlit_app.py` chat box.
2. Streamlit sends `POST http://127.0.0.1:8000/chat` with JSON `{"question": ..., "namespace": ...}` (namespace is set when a PDF is selected).
3. `backend/main.py` sets `agent.ACTIVE_NAMESPACE = request.namespace` and calls `agent.agent.invoke(...)`.
4. The agent (LLM + `prompt.py`) decides the next action. If it chooses scheduling, it calls `create_calendar_event(title, date, time, duration_minutes)`.
5. `tools/calendar_tool.create_calendar_event` validates inputs, constructs a `datetime`, and calls `services/google_calendar.GoogleCalendarService.check_availability(...)`.
6. If available, it calls `GoogleCalendarService.create_event(...)` which inserts the event into the `primary` calendar in timezone `Asia/Kolkata`.
7. After successful creation, the tool calls `services.gmail_service.GmailService.send_email(...)` to send a confirmation email. The recipient is hardcoded in the code.
8. The tool returns a success string (including `event['htmlLink']`) back to the agent, which returns it as the assistant message to the frontend.

Notes:
- The application only sends outgoing emails; there is no inbound-mail processing implemented.
- The calendar/create_event flow assumes the Google OAuth flow has been completed and `token.json` exists or will be created during interactive auth.

---

## 11. Implementation details worth highlighting

- Namespaces for Pinecone are generated from the PDF filename in `pdf_ingest.upload_pdf_to_pinecone` (lowercase, `.pdf` removed, spaces → `_`). The mapping is persisted in the `documents` Postgres table using `document_db.add_document()`.
- `rag.search_pdf` builds a Pinecone client and index at import time and returns the concatenated `text` fields from search hits.
- `calendar_tool.create_calendar_event` uses `datetime.strptime` checks and returns clear error strings for invalid input.
- Google Calendar events are localized to timezone `Asia/Kolkata` in `services/google_calendar.py`.
- `services/google_auth.py` performs `InstalledAppFlow.run_local_server(...)` when no valid token is found — this is an interactive OAuth flow.

---

## 12. Known gaps observable in the code

- Database schema (table creation SQL) for the `documents` table is not included.
- No background worker or inbound email processing for reading mail is implemented.
- Some environment variable names referenced in scripts are inconsistent (e.g., `NAMESPACE`, `PINECONE_NAMESPACE`, `PINECONE_INDEX_NAME`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`) — review before deployment.
- `credentials.json` is present in the repo; this may be intentional for local dev but should be managed carefully in production.

---

## 13. Where to look for related code

- PDF upload & ingestion: `streamlit_app.py`, `backend/main.py`, `pdf_ingest.py`, `upload_pdf.py`, `document_db.py`, `rag.py`.
- Agent & LLM: `agent.py`, `prompt.py`.
- Calendar & email: `tools/calendar_tool.py`, `services/google_calendar.py`, `services/gmail_service.py`, `services/google_auth.py`.
- Database connection & registry: `database.py`, `document_db.py`.
- FastAPI server entrypoints: `backend/main.py`.
- CLI testing: `app.py`, `test.py`.

---

## 14. Suggested next steps (conservative, code-based)

- Add SQL schema or migration for the `documents` table used by `document_db.py`.
- Consolidate environment variable names in `config.py` and across scripts (`PINECONE_NAMESPACE` vs `NAMESPACE`).
- Consider making the email recipient configurable (do not hardcode addresses in `calendar_tool.py`).
- Add minimal developer README with run instructions and required env vars (not included because execution commands are not present in the source).

---

End of PROJECT_DOCUMENTATION.md
