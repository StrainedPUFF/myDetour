import React, { createContext, useContext, useState, useEffect } from 'react';
import FetchSessionData from './FetchSessionData'; // Adjust the path if needed

const SessionContext = createContext();

export const SessionProvider = ({ children }) => {
  const [sessionData, setSessionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleSessionData = (data) => {
    setSessionData({
      sessionId: data.id,
      documentUrl: data.document,
      quiz_id: data.quiz_id,
      userRole: data.host === data.current_user ? "host" : "observer", // Compare dynamically
    });
    setLoading(false); // Set loading to false once data is received
  };

  const handleError = (error) => {
    setError(error);
    setLoading(false); // Set loading to false on error
  };

  useEffect(() => {
    // You can also handle cleanup or additional logic here if needed
  }, []);

  return (
    <>
      <FetchSessionData onSessionData={handleSessionData} onError={handleError} />
      {loading && <p>Loading session...</p>}
      {error && <p style={{ color: 'red' }}>Error: {error.message}</p>}
      {sessionData && (
        <SessionContext.Provider value={sessionData}>
          {children}
        </SessionContext.Provider>
      )}
    </>
  );
};

// Hook to access the SessionContext
export const useSession = () => useContext(SessionContext);