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
        output_file: str = "response.mp3"
    ):

        response = self.client.speak.v1.audio.generate(
            text=text,
            model="aura-2-thalia-en"
        )

        with open(
            output_file,
            "wb"
        ) as file:

            for chunk in response:

                file.write(chunk)

        return output_file
    
