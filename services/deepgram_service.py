import os
import time
import tempfile

from deepgram import DeepgramClient
from config import DEEPGRAM_API_KEY
class DeepgramService:

    def __init__(self):

        self.client = DeepgramClient(
            api_key=DEEPGRAM_API_KEY
        )

    def speech_to_text(
        self,
        audio_file_path: str
    ) -> str:

        with open(audio_file_path, "rb") as file:
            buffer = file.read()

        response = self.client.listen.v1.media.transcribe_file(
            request=buffer,
            model="nova-3",
            smart_format=True,
            punctuate=True
        )

        return (
            response.results
            .channels[0]
            .alternatives[0]
            .transcript
        )

    def text_to_speech(
        self,
        text: str,
        max_retries: int = 3
    ) -> str:

        """
        Convert text to speech using Deepgram.

        Retries temporary Deepgram/network failures
        up to max_retries times.

        A unique temporary MP3 file is created for
        every TTS response.
        """

        if not text or not text.strip():

            raise ValueError(
                "Cannot generate speech from empty text."
            )


        # -------------------------
        # Create Unique Audio File
        # -------------------------

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        )

        output_file = temp_file.name

        temp_file.close()


        # -------------------------
        # Try Deepgram TTS
        # -------------------------

        for attempt in range(
            1,
            max_retries + 1
        ):

            try:

                print(
                    f"TTS attempt {attempt}/{max_retries}"
                )

                response = (
                    self.client
                    .speak
                    .v1
                    .audio
                    .generate(
                        text=text,
                        model="aura-2-thalia-en"
                    )
                )


                # -------------------------
                # Write Audio
                # -------------------------

                with open(
                    output_file,
                    "wb"
                ) as file:

                    for chunk in response:

                        file.write(
                            chunk
                        )


                # -------------------------
                # Validate Audio File
                # -------------------------

                if (
                    not os.path.exists(
                        output_file
                    )
                    or
                    os.path.getsize(
                        output_file
                    ) == 0
                ):

                    raise RuntimeError(
                        "Deepgram returned an empty audio file."
                    )


                print(
                    "TTS generation successful"
                )

                return output_file


            except Exception as e:

                print(
                    f"TTS attempt {attempt} failed:"
                )

                print(
                    str(e)
                )


                # -------------------------
                # Last Attempt Failed
                # -------------------------

                if attempt == max_retries:

                    if os.path.exists(
                        output_file
                    ):

                        try:

                            os.remove(
                                output_file
                            )

                        except OSError:

                            pass

                    raise


                # -------------------------
                # Wait Before Retry
                # -------------------------

                time.sleep(
                    attempt
                )
