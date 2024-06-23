import { ReactNode } from 'react';
import { withStreamlitConnection, StreamlitComponentBase, Streamlit } from "streamlit-component-lib";
import { ReactMic } from 'react-mic';
import './styles.css'; // Make sure to include this line to import your CSS

declare global {
    interface Window {
        webkitAudioContext?: typeof AudioContext;
    }
}

interface ReactMicStopEvent {
    blob: Blob;
    startTime: string;
    stopTime: string;
    options: {
        audioBitsPerSecond: number;
        mimeType: string;
    };
    blobURL: string;
    size: number; // Add size property
    type: string; // Add type property
    arrayBuffer: () => Promise<ArrayBuffer>; // Add arrayBuffer method
    slice: (start?: number, end?: number, contentType?: string) => Blob; // Add slice method
}

class AudioRecorder extends StreamlitComponentBase {
    public state = { isRecording: false, silentDuration: 0, voiceDetected: false }
    private audioContext?: AudioContext;
    private analyser?: AnalyserNode;
    private dataArray?: Uint8Array;
    private silenceThreshold: number = 5; // Adjust the threshold as needed
    private silenceTimeout: number = 0.5; // Seconds of silence to detect
    private minVoiceFrequency: number = 300; // Minimum frequency for human voice in Hz
    private maxVoiceFrequency: number = 3400; // Maximum frequency for human voice in Hz
    private currentRecordedData?: Blob;

    constructor(props: any) {
        super(props);
        this.onData = this.onData.bind(this);
        this.onStop = this.onStop.bind(this);
        this.startRecording = this.startRecording.bind(this);
        this.stopRecording = this.stopRecording.bind(this);
    }

    public render = (): ReactNode => {
        return (
            <div>
                <button onClick={this.startRecording} type="button">Start</button>
                <button onClick={this.stopRecording} type="button">Stop</button>
                <ReactMic
                    record={this.state.isRecording}
                    className="sound-wave"
                    onStop={this.onStop}
                    onData={this.onData}
                    strokeColor="#000000"
                    backgroundColor="#FF4081"
                    visualSetting="frequencyBars"
                />
            </div>
        );
    };

    private startRecording = async (): Promise<void> => {
        this.setState({ isRecording: true });
        //console.log("startRecording entered");
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.initAudioContext(stream);
        } catch (err) {
            console.error('Error accessing microphone:', err);
        }
    }

    private stopRecording = (): void => {
        this.setState({ isRecording: false, silentDuration: 0, voiceDetected: false });
        //console.log("stopRecording entered");
        if (this.audioContext && this.audioContext.state !== "closed") {
            this.audioContext.close();
        }
    }

    private onData(recordedBlob: Blob) {
        this.currentRecordedData = recordedBlob;
    }

    private onStop = async (recordedData: ReactMicStopEvent) => {
        //console.log("onStop entered");
        this.processAudio(recordedData.blob);
    };

    private processAudio = async (recordedBlob: Blob) => {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            const audioContext = new AudioContext({ sampleRate: 16000 });

            const arrayBuffer = await recordedBlob.arrayBuffer();
            const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

            const offlineAudioContext = new OfflineAudioContext(audioBuffer.numberOfChannels, audioBuffer.length, 16000);
            const bufferSource = offlineAudioContext.createBufferSource();
            bufferSource.buffer = audioBuffer;
            bufferSource.connect(offlineAudioContext.destination);
            bufferSource.start(0);

            const renderedBuffer = await offlineAudioContext.startRendering();

            // Convert the rendered buffer to a 16-bit PCM byte array
            const float32Array = renderedBuffer.getChannelData(0);
            const pcmArrayBuffer = new ArrayBuffer(float32Array.length * 2);
            const view = new DataView(pcmArrayBuffer);

            for (let i = 0; i < float32Array.length; i++) {
                const s = Math.max(-1, Math.min(1, float32Array[i]));
                view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true); // true for little-endian
            }

            Streamlit.setComponentValue(pcmArrayBuffer);
        } catch (error) {
            console.error('Error processing audio data:', error);
        }
    };

    private initAudioContext(stream: MediaStream) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.audioContext = new AudioContext();
        this.analyser = this.audioContext.createAnalyser();
        const source = this.audioContext.createMediaStreamSource(stream);
        source.connect(this.analyser);
        this.analyser.fftSize = 2048;
        const bufferLength = this.analyser.frequencyBinCount;
        this.dataArray = new Uint8Array(bufferLength);
        this.monitorSilence();
    }

    private monitorSilence = () => {
        if (!this.analyser || !this.dataArray) return;

        this.analyser.getByteTimeDomainData(this.dataArray);

        const volume = this.getVolume();

        if (volume < this.silenceThreshold) {
            this.setState({ silentDuration: this.state.silentDuration + 1 });
        } else {
            this.setState({ silentDuration: 0, voiceDetected: true });
        }

        if (this.state.voiceDetected && this.state.silentDuration >= this.silenceTimeout * (this.audioContext?.sampleRate ?? 44100) / this.analyser.fftSize) {
            if (this.currentRecordedData) {
                this.stopRecording();
                this.currentRecordedData = undefined;
                this.setState({ voiceDetected: false });
                this.startRecording();
            }
        }

        requestAnimationFrame(this.monitorSilence);
    };

    private getVolume(): number {
        if (!this.analyser || !this.dataArray) return 0;

        this.analyser.getByteFrequencyData(this.dataArray);

        let sum = 0;
        let count = 0;

        // Calculate the average volume in the range of human voice frequencies
        for (let i = 0; i < this.dataArray.length; i++) {
            const frequency = i * (this.audioContext?.sampleRate ?? 44100) / this.analyser.fftSize;
            if (frequency >= this.minVoiceFrequency && frequency <= this.maxVoiceFrequency) {
                sum += this.dataArray[i];
                count++;
            }
        }

        return sum / count;
    }
};

export default withStreamlitConnection(AudioRecorder);
