from contextvars import ContextVar


current_thread_id = ContextVar(
    "current_thread_id",
    default=None
)


def set_current_thread_id(
    thread_id: str
):

    current_thread_id.set(
        thread_id
    )


def get_current_thread_id():

    return current_thread_id.get()