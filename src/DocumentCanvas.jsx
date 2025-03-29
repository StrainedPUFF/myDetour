import React, { useRef, useEffect, useState } from "react";
import { Stage, Layer, Image, Line } from "react-konva";
import * as pdfjs from "pdfjs-dist";
import { useSession } from "./SessionContext";

pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/5.0.375/pdf.worker.mjs`;

const DocumentCanvas = () => {
  const { sessionId, documentUrl } = useSession(); // Access userRole directly
  const { userRole } = useSession();
  const stageRef = useRef();
  const socket = useRef(null);
  const [image, setImage] = useState(null);
  const [lines, setLines] = useState([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const [color, setColor] = useState("black");
  const [isErasing, setIsErasing] = useState(false);
  const [strokeWidth, setStrokeWidth] = useState(2);
  const [pdf, setPdf] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [viewport, setViewport] = useState(null);
  const canDraw = userRole === "host"; // Determine permission directly in DocumentCanvas

  console.log("User Role in DocumentCanvas:", userRole);
  console.log("Can Draw:", userRole === "host");

  const normalizeColor = (color) => {
    const namedColors = { black: "#000000", white: "#FFFFFF", red: "#FF0000" };
    return namedColors[color] || color;
  };

  useEffect(() => {
    const renderPDF = async () => {
      if (!documentUrl) return;

      try {
        const pdfDoc = await pdfjs.getDocument(documentUrl).promise;
        setPdf(pdfDoc);
        setTotalPages(pdfDoc.numPages);
        await renderPage(pdfDoc, currentPage);
      } catch (error) {
        console.error("Error rendering PDF:", error);
      }
    };

    renderPDF();
  }, [documentUrl, currentPage]);

  const renderPage = async (pdfDoc, pageNumber) => {
    const page = await pdfDoc.getPage(pageNumber);
    const viewport = page.getViewport({ scale: 1.5 });
    setViewport(viewport);

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    canvas.width = viewport.width;
    canvas.height = viewport.height;

    await page.render({ canvasContext: context, viewport }).promise;

    const img = new window.Image();
    img.src = canvas.toDataURL();
    img.onload = () => setImage(img);
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) setCurrentPage(currentPage + 1);
  };

  const handlePrevPage = () => {
    if (currentPage > 1) setCurrentPage(currentPage - 1);
  };

  useEffect(() => {
    if (!sessionId) return;

    const webSocketUrl = `ws://127.0.0.1:8080/ws/session/${sessionId}/`;

    socket.current = new WebSocket(webSocketUrl);

    socket.current.onopen = () => console.log("WebSocket connection established.");
    socket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "draw") {
        setLines((prevLines) => [...prevLines, data.payload]);
      }
    };

    socket.current.onclose = () => console.warn("WebSocket connection closed.");
    socket.current.onerror = (error) => console.error("WebSocket error:", error.message);

    return () => {
      if (socket.current) socket.current.close();
    };
  }, [sessionId]);

  const throttle = (func, limit) => {
    let inThrottle;
    return function (...args) {
      if (!inThrottle) {
        func(...args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  };

  const handleMouseDown = () => {
    if (!canDraw) return; // Drawing restricted to hosts
    setIsDrawing(true);
    if (!isErasing) {
      setLines([
        ...lines,
        { points: [], color: normalizeColor(color), strokeWidth },
      ]);
    }
  };

  const handleMouseMove = throttle((e) => {
    if (!isDrawing || !canDraw) return; // Restrict drawing
    const stage = stageRef.current;
    const point = stage.getPointerPosition();

    if (isErasing) {
      const eraserRadius = 10;
      setLines((prevLines) =>
        prevLines.map((line) => ({
          ...line,
          points: line.points.filter(
            (p) => Math.hypot(p.x - point.x, p.y - point.y) > eraserRadius
          ),
        }))
      );
    } else {
      const lastLine = lines[lines.length - 1];
      lastLine.points.push(point);
      lines.splice(lines.length - 1, 1, lastLine);
      setLines([...lines]);
    }
  }, 50);

  const handleMouseUp = () => {
    setIsDrawing(false);
    if (!canDraw || isErasing) return;

    if (socket.current && socket.current.readyState === WebSocket.OPEN) {
      const lastLine = lines[lines.length - 1];
      socket.current.send(
        JSON.stringify({
          type: "draw",
          payload: lastLine,
        })
      );
    }
  };

  const handleUndo = () => {
    if (canDraw) setLines(lines.slice(0, -1));
  };

  return (
    <div>
      <div>
        <button onClick={handlePrevPage} disabled={currentPage === 1}>
          Previous
        </button>
        <button onClick={handleNextPage} disabled={currentPage === totalPages}>
          Next
        </button>
      </div>
      <div>
        <label htmlFor="colorPicker">Choose a color: </label>
        <input
          id="colorPicker"
          type="color"
          value={color}
          onChange={(e) => setColor(e.target.value)}
          disabled={!canDraw} // Disable for non-hosts
        />
        <button onClick={() => setIsErasing(!isErasing)} disabled={!canDraw}>
          {isErasing ? "Stop Erasing" : "Erase"}
        </button>
        <label htmlFor="strokeWidth">Stroke Width: </label>
        <input
          id="strokeWidth"
          type="range"
          min="1"
          max="20"
          value={strokeWidth}
          onChange={(e) => setStrokeWidth(Number(e.target.value))}
          disabled={!canDraw} // Disable for non-hosts
        />
        <button onClick={handleUndo} disabled={!canDraw || lines.length === 0}>
          Undo
        </button>
      </div>
      <Stage
        width={viewport ? viewport.width : 800}
        height={viewport ? viewport.height : 600}
        ref={stageRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        <Layer>
          {image && <Image image={image} />}
          {lines.map((line, i) => (
            <Line
              key={i}
              points={line.points.flatMap((point) => [point.x, point.y])}
              stroke={line.color}
              strokeWidth={line.strokeWidth}
              tension={0.5}
              lineCap="round"
              lineJoin="round"
            />
          ))}
        </Layer>
      </Stage>
    </div>
  );
};

export default DocumentCanvas;
