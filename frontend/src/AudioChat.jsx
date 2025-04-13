import React, { useRef, useEffect, useCallback, useState } from 'react';
import { useSession } from './SessionContext';
import "./AudioChat.css";

const AudioChat = () => {
  const { sessionId } = useSession();
  const audioRef = useRef(null);
  const socket = useRef(null);
  const [isMuted, setIsMuted] = useState(false);
  const [muteOutgoing, setMuteOutgoing] = useState(false);
  const audioContextRef = useRef(null); // Create audioContextRef with useRef

  // Utility to convert PCM data to WAV format
  const createWAV = (pcmData) => {
    const sampleRate = 44100; // Example sample rate
    const numChannels = 1; // Mono audio

    const wavHeader = new Uint8Array(44); // RIFF header size
    const wavBody = new Float32Array(pcmData);

    // Fill WAV header
    const dataSize = wavBody.length * 2; // PCM data size (bytes)
    const totalSize = dataSize + 44;

    const dataView = new DataView(wavHeader.buffer);
    dataView.setUint32(0, 0x52494646); // "RIFF"
    dataView.setUint32(4, totalSize - 8, true); // File size - 8
    dataView.setUint32(8, 0x57415645); // "WAVE"
    dataView.setUint32(12, 0x666d7420); // "fmt "
    dataView.setUint32(16, 16, true); // PCM chunk size
    dataView.setUint16(20, 1, true); // Audio format (1=PCM)
    dataView.setUint16(22, numChannels, true); // Number of channels
    dataView.setUint32(24, sampleRate, true); // Sample rate
    dataView.setUint32(28, sampleRate * numChannels * 2, true); // Byte rate
    dataView.setUint16(32, numChannels * 2, true); // Block align
    dataView.setUint16(34, 16, true); // Bits per sample
    dataView.setUint32(36, 0x64617461); // "data"
    dataView.setUint32(40, dataSize, true); // PCM data size

    return new Blob([wavHeader, new Uint16Array(wavBody.map(x => x * 32767))], { type: 'audio/wav' });
  };

  const playAudio = useCallback((pcmData) => {
    try {
      const floatArray = new Float32Array(Object.values(pcmData));
      const wavBlob = createWAV(floatArray);

      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }

      if (audioContextRef.current.state === 'suspended') {
        audioContextRef.current.resume();
      }

      const reader = new FileReader();
      reader.onload = () => {
        const arrayBuffer = reader.result;

        audioContextRef.current.decodeAudioData(arrayBuffer).then((decodedData) => {
          const source = audioContextRef.current.createBufferSource();
          source.buffer = decodedData;
          source.connect(audioContextRef.current.destination);
          source.start();
        }).catch((error) => {
          console.error("Error decoding audio data:", error);
        });
      };

      reader.readAsArrayBuffer(wavBlob);
    } catch (error) {
      console.error("Error playing audio:", error.message);
    }
  }, []);

  const connectWebSocket = useCallback(() => {
    if (!sessionId) {
      console.error('Session ID is undefined. Unable to initialize WebSocket.');
      return;
    }

    socket.current = new WebSocket(`ws://mydetour-e22e7c03c4e8.herokuapp.com/ws/session/${sessionId}/`);

    socket.current.onopen = () => {
      console.log('WebSocket connection established');
    };

    socket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'audio') {
        console.log('Audio data received:', data.payload);
        playAudio(data.payload);
      }
    };

    socket.current.onclose = () => {
      console.warn('WebSocket disconnected.');
    };

    socket.current.onerror = (error) => {
      console.error('WebSocket error:', error.message);
    };
  }, [sessionId, playAudio]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      socket.current?.close();
    };
  }, [connectWebSocket]);

  const startAudioCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioRef.current.srcObject = stream;

      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }

      await audioContextRef.current.audioWorklet.addModule('audio-processor.js');
      const audioProcessor = new AudioWorkletNode(audioContextRef.current, 'audio-processor');

      const input = audioContextRef.current.createMediaStreamSource(stream);
      input.connect(audioProcessor);
      audioProcessor.connect(audioContextRef.current.destination);

      audioProcessor.port.onmessage = (event) => {
        const audioChunk = event.data;
        if (socket.current && !muteOutgoing) { // Check muteOutgoing state
          socket.current.send(
            JSON.stringify({
              type: 'audio',
              payload: audioChunk,
            })
          );
        }
      };
    } catch (error) {
      console.error('Error capturing audio:', error.message);
    }
  };

  const toggleMute = () => {
    if (audioRef.current?.srcObject) {
      const audioTracks = audioRef.current.srcObject.getAudioTracks();
  
      if (isMuted) {
        // Unmute: Re-enable audio tracks
        audioTracks.forEach((track) => (track.enabled = true));
  
        // Resume audio context if suspended
        if (audioContextRef.state === 'suspended') {
          audioContextRef.resume();
        }
      } else {
        // Mute: Disable audio tracks
        audioTracks.forEach((track) => (track.enabled = false));
  
        // Suspend audio context
        if (audioContextRef.state === 'running') {
          audioContextRef.suspend();
        }
      }
  
      setIsMuted(!isMuted);
    }
  };  

  return (
    <div>
      <audio ref={audioRef} autoPlay />
      <button onClick={toggleMute}>{isMuted ? 'Unmute' : 'Mute'}</button>
      <button onClick={startAudioCapture}>Start Audio</button>
    </div>
  );
};

export default AudioChat;
