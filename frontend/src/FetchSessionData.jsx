import React, { useState, useEffect } from 'react';

const FetchSessionData = ({ onSessionData }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasFetched, setHasFetched] = useState(false); // Ensure data is fetched only once

  useEffect(() => {
    if (typeof onSessionData !== 'function') {
      console.error('onSessionData prop is required and must be a function.');
      return;
    }

    if (hasFetched) {
      return; // Prevent duplicate fetches
    }

    const fetchData = async () => {
      try {
        console.log('Fetching session data...');
        
        const response = await fetch('https://mydetour-e22e7c03c4e8.herokuapp.com/api/get-session-id/', {
          credentials: 'include', // Include authentication credentials
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch session data: ${response.status}`);
        }

        const data = await response.json();

        if (!data || !data.id) {
          throw new Error(`Session ID is missing in the response. Data: ${JSON.stringify(data)}`);
        }

        console.log('Fetched session data:', data);
        onSessionData(data); // Pass fetched data to the parent
        setError(null);
        setHasFetched(true); // Mark as fetched
      } catch (err) {
        const errorMessage =
          err instanceof Error
            ? err.message
            : typeof err === 'string'
            ? err
            : err?.error || JSON.stringify(err);

        console.error('Error fetching session data:', errorMessage);
        setError(errorMessage);
      } finally {
        setLoading(false); // Ensure loading state is stopped
      }
    };

    fetchData();
  }, [onSessionData, hasFetched]);

  if (loading) {
    return <p>Loading session data...</p>;
  }

  if (error) {
    return (
      <div style={{ color: 'red', padding: '10px', border: '1px solid red' }}>
        <p>Error: {error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return null; // No UI as its purpose is fetching
};

export default FetchSessionData;
