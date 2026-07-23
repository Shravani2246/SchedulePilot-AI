from langchain_groq import ChatGroq
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from rag import search_pdf

from tools.calendar_tool import (
    create_calendar_event,
    list_calendar_events
)

from config import (
    GROQ_API_KEY,
    GROQ_MODEL
)

from prompt import SYSTEM_PROMPT


ACTIVE_NAMESPACE = None


# -------------------------
# LLM
# -------------------------

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    temperature=0
)


# -------------------------
# TOOLS
# -------------------------

@tool
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers.
    """

    print(
        "TOOL CALLED: multiply"
    )

    return a * b

@tool
def current_time() -> str:
    """
    Get the current local date and time.

    Use this tool when the user asks for the current time,
    today's date, or when another tool needs today's date
    to resolve relative dates such as today or tomorrow.
    """

    print(
        "TOOL CALLED: current_time"
    )

    from datetime import datetime

    now = datetime.now()

    return now.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

@tool
def pdf_search(question: str) -> str:
    """
    Search uploaded PDF.
    """

    global ACTIVE_NAMESPACE

    if ACTIVE_NAMESPACE is None:

        return "No PDF uploaded."

    print(
        "\nTOOL CALLED: pdf_search"
    )

    print(
        "QUESTION:",
        question
    )

    print(
        "NAMESPACE:",
        ACTIVE_NAMESPACE
    )

    return search_pdf(
        question,
        ACTIVE_NAMESPACE
    )


# -------------------------
# TOOL LIST
# -------------------------

tools = [
    multiply,
    current_time,
    pdf_search,
    create_calendar_event,
    list_calendar_events
]


# -------------------------
# AGENT
# -------------------------

memory = MemorySaver()


agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT,
    checkpointer=memory
)