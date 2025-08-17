import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./Login";
import Signup from "./Signup";
import Dashboard from "./Dashboard";

function App() {
  const [currentUsername, setCurrentUsername] = useState(null);

  const handleLoginSuccess = (username) => {
    setCurrentUsername(username);
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            currentUsername ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Login onLoginSuccess={handleLoginSuccess} />
            )
          }
        />
        <Route path="/signup" element={<Signup />} />
        <Route
          path="/dashboard"
          element={
            currentUsername ? (
              <Dashboard username={currentUsername} />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
