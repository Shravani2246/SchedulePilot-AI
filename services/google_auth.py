from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# -------------------------
# Google OAuth Scopes
# -------------------------

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
]

# -------------------------
# File Paths
# -------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def authenticate_google():
    """
    Authenticate the user with Google OAuth.

    Returns:
        Credentials object.
    """

    creds = None

    # Load saved token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SCOPES
        )

    # If credentials are invalid or expired
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES
            )

            creds = flow.run_local_server(
                port=0,
                open_browser=True
            )

        # Save token for future logins
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds