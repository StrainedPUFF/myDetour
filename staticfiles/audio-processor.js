class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = [];
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (input && input.length > 0) {
      const channelData = input[0];

      // Send the audio data to the main thread
      this.port.postMessage(channelData);
    }

    return true; // Keep processor running
  }
}

registerProcessor('audio-processor', AudioProcessor);
