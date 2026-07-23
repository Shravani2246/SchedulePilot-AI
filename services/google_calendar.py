from datetime import datetime, timedelta

import pytz
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from services.google_auth import authenticate_google


# -------------------------
# Google Calendar Service
# -------------------------

class GoogleCalendarService:

    def __init__(self):

        credentials = authenticate_google()

        self.service = build(
            "calendar",
            "v3",
            credentials=credentials
        )

    def create_event(
        self,
        title: str,
        start_datetime: datetime,
        duration_minutes: int = 60,
        description: str = "",
        location: str = ""
    ):

        india_timezone = pytz.timezone("Asia/Kolkata")

        start_datetime = india_timezone.localize(start_datetime)

        end_datetime = (
            start_datetime +
            timedelta(minutes=duration_minutes)
        )

        event = {

            "summary": title,

            "location": location,

            "description": description,

            "start": {

                "dateTime": start_datetime.isoformat(),

                "timeZone": "Asia/Kolkata"

            },

            "end": {

                "dateTime": end_datetime.isoformat(),

                "timeZone": "Asia/Kolkata"

            }

        }

        created_event = (
            self.service.events()
            .insert(
                calendarId="primary",
                body=event
            )
            .execute()
        )

        return created_event
    
    def check_availability(
        self,
        start_datetime: datetime,
        duration_minutes: int
    ):
        """
        Check whether the requested time slot is free.
        Returns True if available.
        Returns False if another event overlaps.
        """

        india_timezone = pytz.timezone("Asia/Kolkata")

        start_datetime = india_timezone.localize(start_datetime)

        end_datetime = (
            start_datetime +
            timedelta(minutes=duration_minutes)
        )

        try:

            events = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=start_datetime.isoformat(),
                    timeMax=end_datetime.isoformat(),
                    singleEvents=True,
                    orderBy="startTime"
                )
                .execute()
            )

            return len(events.get("items", [])) == 0

        except HttpError as e:

            raise Exception(
                f"Google Calendar Error: {str(e)}"
            )
        
    def list_events(
        self,
        start_datetime: datetime,
        end_datetime: datetime
    ):
        """
        Get Google Calendar events between
        start_datetime and end_datetime.
        """

        india_timezone = pytz.timezone(
            "Asia/Kolkata"
        )

        # -------------------------
        # Localize Start DateTime
        # -------------------------

        start_datetime = india_timezone.localize(
            start_datetime
        )

        # -------------------------
        # Localize End DateTime
        # -------------------------

        end_datetime = india_timezone.localize(
            end_datetime
        )

        try:

            # -------------------------
            # Fetch Calendar Events
            # -------------------------

            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",

                    timeMin=start_datetime.isoformat(),

                    timeMax=end_datetime.isoformat(),

                    singleEvents=True,

                    orderBy="startTime"
                )
                .execute()
            )

            events = events_result.get(
                "items",
                []
            )

            return events

        except HttpError as e:

            raise Exception(
                f"Google Calendar Error: {str(e)}"
            )
        
