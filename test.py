import asyncio
import os
import tempfile

import websockets
from playsound import playsound
from websockets.exceptions import ConnectionClosed

async def main():

    async with websockets.connect(
        "ws://127.0.0.1:8000/voice",
        ping_interval=None
    ) as websocket:

        print(
            "Connected to SchedulePilot AI"
        )

        print(
            "Type 'exit' to quit.\n"
        )

        while True:

            message = input(
                "You: "
            )

            if message.lower() == "exit":

                break

            await websocket.send(
                message
            )

            try:

                response = await websocket.recv()

            except ConnectionClosed as e:

                print(
                    f"\nConnection closed: {e}\n"
                )

                break

            # -------------------------
            # Handle Server Text/Error
            # -------------------------

            if isinstance(
                response,
                str
            ):

                print(
                    "\nServer message:",
                    response,
                    "\n"
                )

                continue


            # -------------------------
            # Audio Received
            # -------------------------

            audio_bytes = response

            print(
                "\nAudio received:",
                len(audio_bytes),
                "bytes"
            )


            # -------------------------
            # Create Unique Temp MP3
            # -------------------------

            temp_file = tempfile.NamedTemporaryFile(
                suffix=".mp3",
                delete=False
            )

            audio_path = temp_file.name

            try:

                temp_file.write(
                    audio_bytes
                )

                temp_file.close()

                print(
                    "AI is speaking...\n"
                )


                # -------------------------
                # Play Audio
                # -------------------------

                await asyncio.to_thread(
                    playsound,
                    audio_path
                )

            except Exception as e:

                print(
                    "\nAudio playback error:",
                    e,
                    "\n"
                )

            finally:

                # -------------------------
                # Delete Temporary MP3
                # -------------------------

                try:

                    if os.path.exists(
                        audio_path
                    ):

                        os.remove(
                            audio_path
                        )

                except PermissionError:

                    print(
                        "Temporary audio file is still locked."
                    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )