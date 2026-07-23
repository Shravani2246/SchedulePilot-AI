from agent import current_time


def main():

    print(
        "Testing current_time tool..."
    )

    result = current_time.invoke(
        {}
    )

    print(
        "Tool result:",
        result
    )


if __name__ == "__main__":

    main()