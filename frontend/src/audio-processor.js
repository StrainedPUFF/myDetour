class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = [];
    this.chunkSize = 512; // Optimized chunk size
  }

  process(inputs) {
    const input = inputs[0];

    if (input && input.length > 0) {
      const channelData = input[0]; // Assuming mono audio

      // Add incoming data to the buffer
      this.buffer.push(...channelData);

      // Process and send audio data in chunks
      while (this.buffer.length >= this.chunkSize) {
        const chunk = this.buffer.slice(0, this.chunkSize);
        this.port.postMessage(chunk); // Send chunk to the main thread
        this.buffer = this.buffer.slice(this.chunkSize); // Remove processed chunk from buffer
      }
    } else {
      console.warn("AudioProcessor: No input detected or empty input array.");
    }

    return true; // Keep processor running
  }
}

registerProcessor('audio-processor', AudioProcessor);
