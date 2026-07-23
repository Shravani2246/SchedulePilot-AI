from agent import agent

while True:

    query = input("You: ")

    if query.lower() == "exit":
        break

    response = agent.invoke(
        {
            "messages": [
                (
                    "user",
                    query
                )
            ]
        },
        config={
            "configurable": {
                "thread_id": "user_1"
            }
        }
    )

    answer = response["messages"][-1].content

    print("\nBot:", answer)
    print()