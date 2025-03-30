import React, { useRef, useEffect } from "react";

const TestCanvas = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const fabric = require("fabric").fabric; // Import fabric here
    if (canvasRef.current) {
      new fabric.Canvas(canvasRef.current, {
        width: 800,
        height: 600,
      });
    }
  }, []);

  return <canvas ref={canvasRef} />;
};

export default TestCanvas;
