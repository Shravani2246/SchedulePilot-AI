from datetime import datetime, timedelta

from langchain.tools import tool

from services.google_calendar import GoogleCalendarService
from services.gmail_service import GmailService

from schedule_db import (
    save_scheduled_meeting
)

from services.runtime_context import (
    get_current_thread_id
)


calendar_service = GoogleCalendarService()

gmail_service = GmailService()


@tool
def create_calendar_event(
    title: str,
    date: str,
    time: str,
    duration_minutes: int
) -> str:
    """
    Create a Google Calendar event.

    Use this tool whenever the user wants to:

    - schedule a meeting
    - create a meeting
    - book an appointment
    - add an event
    - create a calendar event

    Arguments:

    title:
    A descriptive meeting title.

    date:
    Format YYYY-MM-DD.

    time:
    24-hour format HH:MM.

    duration_minutes:
    Length of the meeting.

    Do not call this tool until all required information is available.
    """

    # -------------------------
    # Validate Date
    # -------------------------

    try:

        datetime.strptime(
            date,
            "%Y-%m-%d"
        )

    except ValueError:

        return (
            "Invalid date format.\n"
            "Please use YYYY-MM-DD."
        )


    # -------------------------
    # Validate Time
    # -------------------------

    try:

        datetime.strptime(
            time,
            "%H:%M"
        )

    except ValueError:

        return (
            "Invalid time format.\n"
            "Please use HH:MM in 24-hour format."
        )


    # -------------------------
    # Validate Duration
    # -------------------------

    if duration_minutes <= 0:

        return (
            "Duration must be greater than zero."
        )


    try:

        meeting_datetime = datetime.combine(
            datetime.strptime(
                date,
                "%Y-%m-%d"
            ).date(),
            datetime.strptime(
                time,
                "%H:%M"
            ).time()
        )


        # -------------------------
        # Check Availability
        # -------------------------

        available = calendar_service.check_availability(

            start_datetime=meeting_datetime,

            duration_minutes=duration_minutes

        )


        if not available:

            return (
                "❌ The requested time slot is not available.\n\n"
                f"Date: {date}\n"
                f"Time: {time}\n"
                f"Duration: {duration_minutes} minutes\n\n"
                "Please choose another time."
            )


        # -------------------------
        # Create Event
        # -------------------------

        event = calendar_service.create_event(

            title=title,

            start_datetime=meeting_datetime,

            duration_minutes=duration_minutes

        )


        # -------------------------
        # Save Scheduled Meeting
        # -------------------------

        thread_id = get_current_thread_id()


        if thread_id is not None:

            save_scheduled_meeting(

                thread_id=thread_id,

                google_event_id=event["id"],

                title=title,

                meeting_date=date,

                meeting_time=time,

                duration_minutes=duration_minutes,

                calendar_link=event["htmlLink"]

            )


        # -------------------------
        # Send Confirmation Email
        # -------------------------

        gmail_service.send_email(

            to="shravanisonawane22@gmail.com",

            subject="Meeting Scheduled Successfully",

            body=(
                f"Your meeting has been scheduled.\n\n"
                f"Title: {title}\n"
                f"Date: {date}\n"
                f"Time: {time}\n"
                f"Duration: {duration_minutes} minutes\n\n"
                f"Calendar Link:\n"
                f"{event['htmlLink']}"
            )

        )


        # -------------------------
        # Return Tool Result
        # -------------------------

        return (
            f"Meeting scheduled successfully.\n\n"
            f"Title: {title}\n"
            f"Date: {date}\n"
            f"Time: {time}\n"
            f"Duration: {duration_minutes} minutes\n\n"
            f"Google Calendar Link:\n"
            f"{event['htmlLink']}"
        )


    except Exception as e:

        return (
            f"Error creating event: {str(e)}"
        )
    
@tool
def list_calendar_events(
    period: str
) -> str:
    """
    Read Google Calendar events.

    Use this tool when the user asks:

    - what meetings do I have today
    - show my calendar today
    - what do I have tomorrow
    - show tomorrow's meetings
    - show my meetings this week
    - what is on my calendar this week

    Arguments:

    period:
    Must be one of:

    today
    tomorrow
    this_week
    """
    print(##########
        "TOOL CALLED: list_calendar_events"
    )

    print(
        "PERIOD:",
        period
    )########

    # -------------------------
    # Current Date
    # -------------------------

    now = datetime.now()

    today = now.date()


    # -------------------------
    # Determine Date Range
    # -------------------------

    if period == "today":

        start_date = today

        end_date = (
            today +
            timedelta(days=1)
        )


    elif period == "tomorrow":

        start_date = (
            today +
            timedelta(days=1)
        )

        end_date = (
            today +
            timedelta(days=2)
        )


    elif period == "this_week":

        start_date = today

        end_date = (
            today +
            timedelta(days=7)
        )


    else:

        return (
            "Invalid calendar period.\n"
            "Use today, tomorrow, or this_week."
        )


    # -------------------------
    # Create DateTime Range
    # -------------------------

    start_datetime = datetime.combine(

        start_date,

        datetime.min.time()

    )


    end_datetime = datetime.combine(

        end_date,

        datetime.min.time()

    )


    try:

        # -------------------------
        # Get Calendar Events
        # -------------------------

        events = calendar_service.list_events(

            start_datetime=start_datetime,

            end_datetime=end_datetime

        )


        # -------------------------
        # No Events
        # -------------------------

        if not events:

            return (
                f"No calendar events found for {period}."
            )


        # -------------------------
        # Format Events
        # -------------------------

        formatted_events = []


        for event in events:

            title = event.get(
                "summary",
                "Untitled Event"
            )


            start_data = event.get(
                "start",
                {}
            )


            end_data = event.get(
                "end",
                {}
            )


            calendar_link = event.get(
                "htmlLink",
                ""
            )


            # -------------------------
            # Timed Event
            # -------------------------

            if "dateTime" in start_data:

                start_datetime = datetime.fromisoformat(
                    start_data["dateTime"]
                )


                end_datetime = datetime.fromisoformat(
                    end_data["dateTime"]
                )


                formatted_date = start_datetime.strftime(
                    "%d %B %Y"
                )


                start_time = start_datetime.strftime(
                    "%I:%M %p"
                )


                end_time = end_datetime.strftime(
                    "%I:%M %p"
                )


                formatted_event = (

                    f"Title: {title}\n"

                    f"Date: {formatted_date} | "

                    f"Start Time: {start_time} | "

                    f"End Time: {end_time}\n"

                    f"Calendar Link: {calendar_link}"

                )


            # -------------------------
            # All-Day Event
            # -------------------------

            else:

                event_date = datetime.strptime(
                    start_data["date"],
                    "%Y-%m-%d"
                )


                formatted_date = event_date.strftime(
                    "%d %B %Y"
                )


                formatted_event = (

                    f"Title: {title}\n"

                    f"Date: {formatted_date} | "

                    f"Time: All day\n"

                    f"Calendar Link: {calendar_link}"

                )


            formatted_events.append(
                formatted_event
            )
        # -------------------------
        # Return Events
        # -------------------------

        return (
            "\n\n--------------------\n\n".join(
                formatted_events
            )
        )


    except Exception as e:

        return (
            f"Error reading calendar events: {str(e)}"
        )