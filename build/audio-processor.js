class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
      super();
      this.buffer = [];
    }
  
    // The main audio processing function
    process(inputs, outputs, parameters) {
      const input = inputs[0];
      if (input && input.length > 0) {
        // Assuming mono-channel input (1 channel)
        const channelData = input[0];
  
        // Send the audio data to the main thread
        this.port.postMessage(channelData);
  
        // If you need to manipulate the audio, you can do so here.
        // For example, apply effects, filters, etc.
      }
  
      // Returning true means the processor will keep running
      return true;
    }
  }
  
  // Register the processor
  registerProcessor('audio-processor', AudioProcessor);
  