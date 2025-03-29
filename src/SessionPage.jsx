import React, { useState, useEffect } from 'react';
import DocumentCanvas from './DocumentCanvas';
import AudioChat from './AudioChat';
import { useSession } from './SessionContext';

const SessionPage = () => {
  const { sessionId, documentUrl, quiz_id, userRole } = useSession(); // Still accessing session data for validation
  const [error, setError] = useState('');

  useEffect(() => {
    if (!sessionId) {
      setError("Error: Session ID is undefined.");
    } else if (!documentUrl) {
      setError("Error: No document URL available for this session.");
    } else {
      setError(''); // Clear errors if both sessionId and documentUrl are valid
    }
  }, [sessionId, documentUrl]);

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

 // const isHost = userRole === "host";

  return (
    <div>
      <h1>Session Page</h1>
      <p aria-live="polite">
        {userRole === "host"
          ? "You are the host. You can manage the session and interact with all tools."
          : "You are in observation mode."}
      </p>
      <DocumentCanvas /> 
      <AudioChat sessionId={sessionId} />
      <a href={`http://127.0.0.1:8000/attempt-quiz/${quiz_id}/`}>Go to Quiz</a>
    </div>
  );
};

export default SessionPage;
