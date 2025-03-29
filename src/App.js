import React from 'react';
import './App.css'; // Import specific styles for App
import FetchSessionData from "./FetchSessionData";
import SessionPage from "./SessionPage"
// import TestCanvas from './TestCanvas';



function App() {
  return (
    <div>
      {/* <h1>Welcome to My React App</h1>
      <p>Am still having trouble</p> */}
      < FetchSessionData />
      < SessionPage />
     </div>
  );
}
export default App;
