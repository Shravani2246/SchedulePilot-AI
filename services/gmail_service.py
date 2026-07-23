import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from services.google_auth import authenticate_google


class GmailService:

    def __init__(self):

        credentials = authenticate_google()

        self.service = build(
            "gmail",
            "v1",
            credentials=credentials
        )

    def send_email(
        self,
        to: str,
        subject: str,
        body: str
    ):

        message = MIMEText(body)

        message["to"] = to

        message["subject"] = subject

        raw = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        message = {

            "raw": raw

        }

        sent_message = (
            self.service.users()
            .messages()
            .send(
                userId="me",
                body=message
            )
            .execute()
        )

        return sent_message