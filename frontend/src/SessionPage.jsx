import React, { useState, useEffect } from 'react';
import DocumentCanvas from './DocumentCanvas';
import AudioChat from './AudioChat';
import { useSession } from './SessionContext';
import './SessionPage.css';

const SessionPage = () => {
  const { sessionId, documentUrl, quiz_id, userRole } = useSession();
  const [error, setError] = useState('');

  useEffect(() => {
    if (!sessionId) {
      setError("Error: Session ID is undefined.");
    } else if (!documentUrl) {
      setError("Error: No document URL available for this session.");
    } else {
      setError('');
    }
  }, [sessionId, documentUrl]);

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="session-page">
      <header className="session-header">
        <h1>Session Page</h1>
        <p>
          {userRole === "host"
            ? "You are the host. You can manage the session and interact with all tools."
            : "You are in observation mode."}
        </p>
      </header>
      <main className="session-content">
        <section className="document-section">
          {/* <h2>Document Viewer</h2> */}
          <DocumentCanvas />
        </section>
        <section className="audio-section">
          {/* <h2>Audio Chat</h2> */}
          <AudioChat sessionId={sessionId} />
        </section>
      </main>
      <footer className="session-footer">
        {/* <a className="quiz-button" href={`https://mydetour-e22e7c03c4e8.herokuapp.com/attempt-quiz/${quiz_id}/`}>Go to Quiz</a> */}
        <a className="quiz-button" href={`http://127.0.0.1:8000/attempt-quiz/${quiz_id}/`}>Go to Quiz</a>
      </footer>
    </div>
  );
};

export default SessionPage;
 