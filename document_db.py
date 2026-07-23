from database import get_connection


def add_document(
    filename,
    namespace
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO documents
        (
            filename,
            namespace
        )
        VALUES
        (
            %s,
            %s
        )
        ON CONFLICT
        (
            filename
        )
        DO NOTHING
        """,
        (
            filename,
            namespace
        )
    )

    conn.commit()

    cur.close()

    conn.close()

def load_documents():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            filename,
            namespace
        FROM documents
        """
    )

    rows = cur.fetchall()

    cur.close()

    conn.close()

    return {
        row[0]: row[1]
        for row in rows
    }

def get_namespace(
    filename
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT namespace
        FROM documents
        WHERE filename=%s
        """,
        (
            filename,
        )
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return row[0]

    return None

def document_exists(
    filename
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT id
        FROM documents
        WHERE filename=%s
        """,
        (
            filename,
        )
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row is not None

def delete_document(
    filename
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM documents
        WHERE filename=%s
        """,
        (
            filename,
        )
    )

    conn.commit()

    cur.close()

    conn.close()

