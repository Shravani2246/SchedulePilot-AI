from services.deepgram_service import (
    DeepgramService
)


deepgram = DeepgramService()


audio_file = "test_audio.mp3"


try:

    print(
        "Testing Deepgram Speech-to-Text..."
    )

    transcript = deepgram.speech_to_text(
        audio_file
    )

    print(
        "\nTranscript:"
    )

    print(
        transcript
    )


except FileNotFoundError:

    print(
        "\nERROR: test_audio.mp3 was not found."
    )

    print(
        "Place an MP3 voice recording named "
        "'test_audio.mp3' in the project root."
    )


except Exception as e:

    print(
        "\nSTT ERROR:"
    )

    print(
        str(e)
    )