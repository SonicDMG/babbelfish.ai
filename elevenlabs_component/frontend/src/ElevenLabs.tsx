import React, { useEffect } from "react";
import { withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import { ElevenLabsClient } from "elevenlabs";
import { Buffer } from "buffer";  // Import Buffer

declare global {
    interface Window {
        webkitAudioContext: typeof AudioContext;
    }
}

const XI_API_KEY = "52cd5996ea8b5110695cac30d0db85d1";
const VOICE_ID = "spPbymoy3hffKOFaqQsq";

if (!XI_API_KEY) {
    throw new Error("Missing XI_API_KEY in environment variables");
}

const client = new ElevenLabsClient({
    apiKey: XI_API_KEY,
});

export const createAudioStreamFromText = async (
    text: string
): Promise<Buffer> => {
    console.log("text input from EL component", text);
    const audioStream = await client.generate({
        voice: VOICE_ID,
        model_id: "eleven_multilingual_v2",
        text,
    });

    const chunks: Buffer[] = [];
    for await (const chunk of audioStream) {
        chunks.push(chunk);
    }

    const content = Buffer.concat(chunks);
    return content;
};

const playAudio = async (audioBuffer: Buffer) => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();

    // Convert the Buffer to an ArrayBuffer
    const arrayBuffer = audioBuffer.buffer.slice(audioBuffer.byteOffset, audioBuffer.byteOffset + audioBuffer.byteLength);

    try {
        // Decode the audio data
        const decodedData = await audioContext.decodeAudioData(arrayBuffer);
        
        // Create a buffer source
        const source = audioContext.createBufferSource();
        source.buffer = decodedData;
        source.connect(audioContext.destination);
        source.start(0);
    } catch (error) {
        console.error('Error decoding audio data', error);
    }
};

const ElevenLabs: React.FC<ComponentProps> = ({ args }) => {
    useEffect(() => {
        const fetchAndPlayAudio = async () => {
            const audioBuffer = await createAudioStreamFromText(args.text);
            playAudio(audioBuffer);
        };
        
        fetchAndPlayAudio();
    }, [args.text]);

    return (
        <div>
            <h1>{args.title}</h1>
        </div>
    );
};

export default withStreamlitConnection(ElevenLabs);
