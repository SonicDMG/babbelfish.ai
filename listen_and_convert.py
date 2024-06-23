from collections import deque
import threading
import queue
import speech_recognition as sr
import webrtcvad

class TranscribeAudio:
    """
    A class to handle real-time audio transcription using the Google Web Speech API.

    This class records audio from the microphone in chunks, processes the audio data, and 
    transcribes it using the Google Web Speech API. It operates in real-time, continuously 
    listening and transcribing audio until stopped.

    Attributes:
        samplerate (int): The sample rate for the audio recording.
        frame_duration (int): The duration of each audio chunk to record in milliseconds.
        recognizer (Recognizer): An instance of the Recognizer class for speech recognition.
        is_running (bool): A flag to control the recording loop.
        transcription (str): Stores the latest transcription result.
        condition (Condition): A condition variable to synchronize threads.
        vad (webrtcvad.Vad): An instance of the WebRTC VAD class.
        audio_buffer (list): Buffer to store audio chunks for processing.
    
    Methods:
        recognize_speech_from_mic(audio_data):
            Transcribes speech from recorded audio data.

        record_and_recognize():
            Continuously records audio from the microphone and processes it for transcription.

        process_audio(audio_data):
            Processes the recorded audio data and updates the transcription.

        start():
            Starts the recording and recognition process in a separate thread.

        get_transcription():
            Returns the latest transcription result.

        stop():
            Stops the recording loop.
    """
    def __init__(self, samplerate=16000, frame_duration=30, audio_queue=None):
        self.samplerate = samplerate
        self.frame_duration = frame_duration
        self.frame_size = int(samplerate * frame_duration / 1000)
        self.recognizer = sr.Recognizer()
        self.is_running = False
        self.transcription = None
        self.condition = threading.Condition()
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(1)  # 0: least aggressive, 3: most aggressive
        self.audio_buffer = deque()  # Using deque for efficient appends and pops
        self.ellipses_printed = 0
        self.audio_queue = audio_queue or queue.Queue()


    def recognize_speech_from_mic_as_bytes(self, audio_data):
        """
        Transcribe speech from recorded audio data.

        :param audio_data: The recorded audio data.
        :return: A dictionary with three keys:
                "success": a boolean indicating whether the API request was successful,
                "error":   `None` if no error occurred, otherwise a string containing
                            an error message if the API could not be reached or
                            speech was unrecognizable,
                "transcription": `None` if speech could not be transcribed,
                                otherwise a string containing the transcribed text.
        """
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        try:
            # Create an AudioData object from the bytes
            audio = sr.AudioData(audio_data, 16000, 2)  # Ensure the sample rate and sample width match your audio data

            # Recognize the speech
            transcription = self.recognizer.recognize_google(audio)
            print("transcription from transcriber: ", transcription)
            response["transcription"] = transcription

            if transcription:
                with self.condition:
                    self.transcription = transcription
                    self.condition.notify()
        except sr.RequestError:
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            response["error"] = "Unable to recognize speech"

        return response


    def process_audio(self, audio_data):
        """
        Process the audio data and transcribe it.

        :param audio_data: The recorded audio data.
        :return: The transcribed text.
        """

        print("audio_data from transcriber")
        result = self.recognize_speech_from_mic_as_bytes(audio_data)
        if result["success"]:
            if result["transcription"]:
                return result["transcription"]
        else:
            print("ERROR: {}\n".format(result["error"]))
        return None


    def start(self):
        """
        Starts the recording and recognition process in a separate thread.
        """
        print("Starting transcription from class...")
        self.is_running = True
        #self.thread = threading.Thread(target=self.record_and_recognize)
        #self.thread.start()


    def get_transcription(self):
        """
        Returns the latest transcription result.
        """
        with self.condition:
            self.condition.wait()
            return self.transcription


    def stop(self):
        """
        Stops the recording loop.
        """
        print("Stoppping transcription from class...")
        self.is_running = False
        #self.thread.join()
