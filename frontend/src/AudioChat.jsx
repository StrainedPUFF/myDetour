import React, { useRef, useEffect, useCallback, useState } from 'react';
import { useSession } from './SessionContext';
import "./AudioChat.css";

const AudioChat = () => {
  const { sessionId } = useSession();
  const audioRef = useRef(null);
  const socket = useRef(null);
  const audioContextRef = useRef(null);
  const [isMuted, setIsMuted] = useState(false);

  // Function to play received audio
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

  // Function to connect WebSocket
  const connectWebSocket = useCallback(() => {
    if (!sessionId) {
      console.error('Session ID is undefined. Unable to initialize WebSocket.');
      return;
    }

    socket.current = new WebSocket(`ws://127.0.0.1:8080/ws/session/${sessionId}/`);

    socket.current.onopen = () => {
      console.log('WebSocket connection established');
    };

    // socket.current.onmessage = (event) => {
    //   const data = JSON.parse(event.data);

    //   if (data.type === 'audio') {
    //     console.log('Audio data received:', data.payload);
    //     playAudio(data.payload);
    //   }
    // };
    socket.current.onmessage = async (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "transportCreated") {
        console.log("✅ Transport Created:", data.transportParams);

        // 🔄 Send Transport Connection request
        await socket.current.send(JSON.stringify({
          type: "connectTransport",
          clientId: sessionId,
          dtlsParameters: data.transportParams.dtlsParameters
        }));
      }

      if (data.type === "offerAccepted") {
        console.log("✅ WebRTC Offer Accepted, streaming audio...");
        startAudioCapture(); // 🔄 Start sending audio after transport is ready
      }

      if (data.type === "consumerCreated") {
        console.log("✅ Consumer Created:", data.consumerParams);
        playAudio(data.consumerParams);
      }

      if (data.type === 'audio') {
        console.log('🔊 Audio data received:', data.payload);
        playAudio(data.payload);
      }
    };


    socket.current.onclose = () => {
      console.warn('WebSocket disconnected. Attempting to reconnect...');
      setTimeout(() => connectWebSocket(), 5000); // Reconnect after 5 seconds
    };

    socket.current.onerror = (error) => {
      console.error('WebSocket error:', error.message);
    };
  }, [sessionId, playAudio]);

  useEffect(() => {
    connectWebSocket();
    const audioElement = audioRef.current;
  
    return () => {
      socket.current?.close();
      audioContextRef.current?.close();
      if (audioElement?.srcObject) { // Use the defined variable here
        const tracks = audioElement.srcObject.getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, [connectWebSocket]);
  

  // Function to capture audio from the user's microphone
  const startAudioCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioRef.current.srcObject = stream;

      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }

      await audioContextRef.current.audioWorklet.addModule('.src/audio-processor.js');
      const audioProcessor = new AudioWorkletNode(audioContextRef.current, 'audio-processor');

      const input = audioContextRef.current.createMediaStreamSource(stream);
      input.connect(audioProcessor);

      audioProcessor.port.onmessage = (event) => {
        const audioChunk = event.data;

        if (socket.current && socket.current.readyState === WebSocket.OPEN) {
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

  // Function to toggle mute/unmute
  const toggleMute = () => {
    if (audioRef.current?.srcObject) {
      const audioTracks = audioRef.current.srcObject.getAudioTracks();

      if (isMuted) {
        audioTracks.forEach((track) => (track.enabled = true));
      } else {
        audioTracks.forEach((track) => (track.enabled = false));
      }

      setIsMuted(!isMuted);
    }
  };

  // Utility function to create WAV file
  const createWAV = (pcmData) => {
    const sampleRate = 44100;
    const numChannels = 1;

    const wavHeader = new Uint8Array(44);
    const wavBody = new Float32Array(pcmData);

    const dataSize = wavBody.length * 2;
    const totalSize = dataSize + 44;

    const dataView = new DataView(wavHeader.buffer);
    dataView.setUint32(0, 0x52494646);
    dataView.setUint32(4, totalSize - 8, true);
    dataView.setUint32(8, 0x57415645);
    dataView.setUint32(12, 0x666d7420);
    dataView.setUint32(16, 16, true);
    dataView.setUint16(20, 1, true);
    dataView.setUint16(22, numChannels, true);
    dataView.setUint32(24, sampleRate, true);
    dataView.setUint32(28, sampleRate * numChannels * 2, true);
    dataView.setUint16(32, numChannels * 2, true);
    dataView.setUint16(34, 16, true);
    dataView.setUint32(36, 0x64617461);
    dataView.setUint32(40, dataSize, true);

    return new Blob([wavHeader, new Uint16Array(wavBody.map((x) => x * 32767))], { type: 'audio/wav' });
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
