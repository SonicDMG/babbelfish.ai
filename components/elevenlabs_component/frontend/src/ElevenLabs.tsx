import React, { useEffect } from "react";
import { withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import { ElevenLabsClient } from "elevenlabs";
import { Buffer } from "buffer";  // Import Buffer

declare global {
    interface Window {
        webkitAudioContext: typeof AudioContext;
    }
}

const XI_API_KEY = process.env.XI_API_KEY;

if (!XI_API_KEY) {
    throw new Error("Missing XI_API_KEY in environment variables");
}

const client = new ElevenLabsClient({
    apiKey: XI_API_KEY,
});

export const createAudioStreamFromText = async (
    text: string,
    voice_id: string,
    model_id: string,
): Promise<Buffer> => {
    const audioStream = await client.generate({
        voice: voice_id,
        model_id: model_id,
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
            //console.log("Text inputs from EL component args", args);
            const audioBuffer = await createAudioStreamFromText(args.text, args.voice_id, args.model_id);
            playAudio(audioBuffer);
        };
        
        fetchAndPlayAudio();
    }, [args]);

    return (
        <div>
            <h1>{args.title}</h1>
        </div>
    );
};

export default withStreamlitConnection(ElevenLabs);
