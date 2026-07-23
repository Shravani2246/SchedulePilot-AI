from database import get_connection


def save_conversation_state(
    thread_id,
    meeting_title=None,
    meeting_date=None,
    meeting_time=None,
    duration_minutes=None,
    status="collecting"
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO conversation_state
        (
            thread_id,
            meeting_title,
            meeting_date,
            meeting_time,
            duration_minutes,
            status
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s
        )

        ON CONFLICT(thread_id)

        DO UPDATE SET

            meeting_title=EXCLUDED.meeting_title,

            meeting_date=EXCLUDED.meeting_date,

            meeting_time=EXCLUDED.meeting_time,

            duration_minutes=EXCLUDED.duration_minutes,

            status=EXCLUDED.status,

            updated_at=NOW()
        """,
        (
            thread_id,
            meeting_title,
            meeting_date,
            meeting_time,
            duration_minutes,
            status
        )
    )

    conn.commit()

    cur.close()

    conn.close()

def get_conversation_state(thread_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT

            meeting_title,

            meeting_date,

            meeting_time,

            duration_minutes,

            status

        FROM conversation_state

        WHERE thread_id=%s
        """,
        (
            thread_id,
        )
    )

    row = cur.fetchone()

    cur.close()

    conn.close()

    if row is None:

        return None

    return {

        "meeting_title": row[0],

        "meeting_date": row[1],

        "meeting_time": row[2],

        "duration_minutes": row[3],

        "status": row[4]

    }


def clear_conversation_state(thread_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM conversation_state

        WHERE thread_id=%s
        """,
        (
            thread_id,
        )
    )

    conn.commit()

    cur.close()

    conn.close()


def save_scheduled_meeting(

    thread_id,

    google_event_id,

    title,

    meeting_date,

    meeting_time,

    duration_minutes,

    calendar_link

):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO scheduled_meetings
        (

            thread_id,

            google_event_id,

            title,

            meeting_date,

            meeting_time,

            duration_minutes,

            calendar_link

        )

        VALUES

        (

            %s,%s,%s,%s,%s,%s,%s

        )
        """,
        (

            thread_id,

            google_event_id,

            title,

            meeting_date,

            meeting_time,

            duration_minutes,

            calendar_link

        )
    )

    conn.commit()

    cur.close()

    conn.close()