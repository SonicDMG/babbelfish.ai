import { ReactNode } from 'react';
import { withStreamlitConnection, StreamlitComponentBase, Streamlit } from "streamlit-component-lib";
import { ReactMic } from 'react-mic';
import './styles.css';

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
    size: number;
    type: string;
    arrayBuffer: () => Promise<ArrayBuffer>;
    slice: (start?: number, end?: number, contentType?: string) => Blob;
}

interface AudioRecorderState {
    isRecording: boolean;
    silentDuration: number;
    voiceDetected: boolean;
}

class AudioRecorder extends StreamlitComponentBase<{}, AudioRecorderState> {
    public state: AudioRecorderState = { isRecording: false, silentDuration: 0, voiceDetected: false };
    private audioContext?: AudioContext;
    private analyser?: AnalyserNode;
    private dataArray?: Uint8Array;
    private silenceThreshold: number = 5;
    private silenceTimeout: number = 0.1;
    private minVoiceFrequency: number = 300;
    private maxVoiceFrequency: number = 3400;
    private currentRecordedData?: Blob;
    private noiseGateThreshold: number = -40; // in decibels

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

    private async startRecording(): Promise<void> {
        this.setState({ isRecording: true });
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.initAudioContext(stream);
        } catch (err) {
            console.error('Error accessing microphone:', err);
        }
    }

    private stopRecording(): void {
        this.setState({ isRecording: false, silentDuration: 0, voiceDetected: false });
        if (this.audioContext && this.audioContext.state !== "closed") {
            this.audioContext.close();
        }
    }

    private onData(recordedBlob: Blob): void {
        this.currentRecordedData = recordedBlob;
    }

    private async onStop(recordedData: ReactMicStopEvent): Promise<void> {
        this.processAudio(recordedData.blob);
    }

    private async processAudio(recordedBlob: Blob): Promise<void> {
        try {
            const audioContext = this.createAudioContext();
            const audioBuffer = await this.decodeAudioData(audioContext, recordedBlob);
            const renderedBuffer = await this.applyBandPassFilter(audioBuffer);
            const pcmArrayBuffer = this.convertToPCM(renderedBuffer);

            Streamlit.setComponentValue(pcmArrayBuffer);
        } catch (error) {
            console.error('Error processing audio data:', error);
        }
    }

    private createAudioContext(): AudioContext {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        return new AudioContext({ sampleRate: 16000 });
    }

    private async decodeAudioData(audioContext: AudioContext, recordedBlob: Blob): Promise<AudioBuffer> {
        const arrayBuffer = await recordedBlob.arrayBuffer();
        return await audioContext.decodeAudioData(arrayBuffer);
    }

    private async applyBandPassFilter(audioBuffer: AudioBuffer): Promise<AudioBuffer> {
        const offlineAudioContext = new OfflineAudioContext(audioBuffer.numberOfChannels, audioBuffer.length, 16000);
        const bufferSource = offlineAudioContext.createBufferSource();
        bufferSource.buffer = audioBuffer;

        const bandPassFilter = offlineAudioContext.createBiquadFilter();
        bandPassFilter.type = "bandpass";
        bandPassFilter.frequency.value = (this.minVoiceFrequency + this.maxVoiceFrequency) / 2;
        bandPassFilter.Q.value = (this.maxVoiceFrequency - this.minVoiceFrequency) / (this.minVoiceFrequency + this.maxVoiceFrequency);

        bufferSource.connect(bandPassFilter);
        bandPassFilter.connect(offlineAudioContext.destination);
        bufferSource.start(0);

        return await offlineAudioContext.startRendering();
    }

    private convertToPCM(renderedBuffer: AudioBuffer): ArrayBuffer {
        const float32Array = renderedBuffer.getChannelData(0);
        const pcmArrayBuffer = new ArrayBuffer(float32Array.length * 2);
        const view = new DataView(pcmArrayBuffer);

        for (let i = 0; i < float32Array.length; i++) {
            const s = Math.max(-1, Math.min(1, float32Array[i]));
            view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }

        return pcmArrayBuffer;
    }

    private initAudioContext(stream: MediaStream): void {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.audioContext = new AudioContext();
        this.analyser = this.audioContext.createAnalyser();
        const source = this.audioContext.createMediaStreamSource(stream);

        // Apply noise gate
        const gainNode = this.audioContext.createGain();
        gainNode.gain.value = 0.9; // Adjust gain value as needed
        source.connect(gainNode);
        gainNode.connect(this.analyser);

        this.analyser.fftSize = 256;
        const bufferLength = this.analyser.frequencyBinCount;
        this.dataArray = new Uint8Array(bufferLength);
        this.monitorSilence();
    }

    private monitorSilence = (): void => {
        if (!this.analyser || !this.dataArray) return;

        this.analyser.getByteTimeDomainData(this.dataArray);

        const volume = this.getVolume();

        this.setState(prevState => {
            const silentDuration = volume < this.silenceThreshold ? prevState.silentDuration + 1 : 0;
            const voiceDetected = volume >= this.silenceThreshold;

            if (voiceDetected && silentDuration >= this.silenceTimeout * (this.audioContext?.sampleRate ?? 16000) / this.analyser.fftSize) {
                if (this.currentRecordedData) {
                    this.stopRecording();
                    this.currentRecordedData = undefined;
                    this.startRecording();
                }
            }

            return { silentDuration, voiceDetected };
        });

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

        // Apply noise gate threshold
        const averageVolume = sum / count;
        return averageVolume > this.noiseGateThreshold ? averageVolume : 0;
    }
}

export default withStreamlitConnection(AudioRecorder);
