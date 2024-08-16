"""A class to handle real-time audio transcription using the Google Web Speech API."""
from collections import deque
import threading
import queue
import logging
import numpy as np
import speech_recognition as sr
import webrtcvad
import coloredlogs

# Configure logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO',
                    logger=logger,
                    fmt='%(filename)s %(levelname)s %(message)s',
                    level_styles={
                        'debug': {'color': 'green'},
                        'info': {'color': 'blue'},
                        'warning': {'color': 'yellow'},
                        'error': {'color': 'red'},
                        'critical': {'color': 'magenta'}
                    }
)

class TranscribeAudio:
    """
    This class records audio from the microphone in chunks, processes the audio data, and 
    transcribes it using the Google Web Speech API. It operates in real-time, continuously 
    listening and transcribing audio until stopped.
    """
    def __init__(self, samplerate=16000, frame_duration=30):
        self.samplerate = samplerate
        self.frame_duration = frame_duration
        self.frame_size = int(samplerate * frame_duration / 1000)
        self.recognizer = sr.Recognizer()
        self.is_running = False
        self.transcription = None
        self.condition = threading.Condition()
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)  # 0: least aggressive, 3: most aggressive
        self.audio_buffer = deque()  # Using deque for efficient appends and pops
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.processing_thread = threading.Thread(target=self.process_audio_queue)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def audio_to_numpy(self, audio_data):
        """
        Convert an audio_data bytes object to a numpy array.
        """
        audio_array = np.frombuffer(audio_data, np.int16)
        return audio_array

    def calculate_rms(self, audio_array):
        """
        Calculate the Root Mean Square (RMS) of the audio signal.
        """
        rms = np.sqrt(np.mean(audio_array**2))
        logger.info("Calculated RMS: %s", rms)  # Debug output for RMS
        return rms

    def is_speech_present(self, audio_data, noise_threshold=10):
        """
        Determine if the audio contains speech or just noise.
        """
        audio_array = self.audio_to_numpy(audio_data)
        rms = self.calculate_rms(audio_array)
        logger.info("RMS Energy: %s, Threshold: %s", rms, noise_threshold)  # Debug output for RMS and threshold
        return rms > noise_threshold

    def recognize_speech_from_mic_as_bytes(self, audio_data, speaking_language):
        """
        Transcribe speech from recorded audio data.
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
            logger.info("speaking_language is %s", speaking_language)
            transcription = self.recognizer.recognize_google(audio, language=speaking_language)
            if transcription and transcription != "":
                response["transcription"] = transcription

                with self.condition:
                    self.transcription = transcription
                    self.condition.notify()
        except sr.RequestError:
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            response["error"] = "Unable to recognize speech"

        return response

    def process_audio(self, audio_data, speaking_language):
        """
        Process the audio data and transcribe it.
        """
        if self.is_speech_present(audio_data):
            logger.info("human speech detected from transcriber")
            result = self.recognize_speech_from_mic_as_bytes(audio_data, speaking_language)
            logger.info("recognize_speech_from_mic_as_bytes result: %s", result)
            if result["success"]:
                if result["transcription"]:
                    # Clear the audio buffer after a successful transcription
                    self.audio_buffer.clear()
                    return result["transcription"]
            else:
                logger.error("ERROR: %s", result['error'])
        else:
            logger.info("No meaningful speech detected, just noise")
        return None

    def process_audio_queue(self):
        """
        Continuously processes audio data from the queue.
        """
        while not self.stop_event.is_set():
            try:
                audio_data, speaking_language = self.audio_queue.get(timeout=1)  # Wait for 1 second for new audio data
                if audio_data:
                    self.process_audio(audio_data, speaking_language)
                self.audio_queue.task_done()
            except queue.Empty:
                continue

    def add_audio_to_queue(self, audio_data, speaking_language):
        """
        Adds audio data to the queue for processing.
        """
        self.audio_queue.put((audio_data, speaking_language))

    def start(self):
        """
        Starts the recording and recognition process in a separate thread.
        """
        logger.info("Starting transcription from class...")
        self.is_running = True

    def get_transcription(self):
        """
        Returns the latest transcription result.
        """
        with self.condition:
            self.condition.wait()
            transcription = self.transcription
            self.transcription = None
            return transcription

    def stop(self):
        """
        Stops the recording loop.
        """
        logger.info("Stopping transcription from class...")
        self.is_running = False
        self.stop_event.set()
        self.processing_thread.join()
