import React, { useState } from 'react';
import FetchSessionData from './FetchSessionData';
import SessionPage from './SessionPage';

const App = () => {
  // State management for session data, errors, and loading status
  const [sessionData, setSessionData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Handle the fetched session data
  const handleSessionData = (data) => {
    // Check for valid session data
    if (!data || !data.id || !data.document) {
      setError('Invalid session data received.'); // Set an error if data is invalid
      setLoading(false); // Stop loading
      return;
    }
    setSessionData(data); // Update session data
    setLoading(false); // Stop loading
    setError(null); // Clear any previous errors
  };

  // Render while session data is being fetched
  if (loading) {
    return <FetchSessionData onSessionData={handleSessionData} />;
  }

  // Render error message if fetching session data fails
  if (error || !sessionData || !sessionData.id || !sessionData.document) {
    return (
      <div style={{ color: 'red', padding: '10px', border: '1px solid red' }}>
        <p>Error: {error || 'Unable to load session data.'}</p>
        {/* Provide a retry button for convenience */}
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  // Render the main session page with the fetched session data
  return (
    <SessionPage
      documentUrl={sessionData?.document || 'sessions//default-document.pdf'} // Default document fallback
      sessionId={sessionData?.id} // Pass session ID to child components
    />
  );
};

export default App;
