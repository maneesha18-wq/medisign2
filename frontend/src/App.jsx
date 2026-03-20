import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import './index.css';

// Simple Auth Guard
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* Dashboard Routes with Protected Layout */}
        <Route
          path="/dashboard/*"
          element={
            <ProtectedRoute>
              <DashboardRoutes />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

// Sub-routes for dashboard area
const DashboardRoutes = () => {
  return (
    <Routes>
      <Route index element={<Dashboard />} />
      <Route path="webcam" element={<Dashboard view="webcam" />} />
      <Route path="upload" element={<Dashboard view="upload" />} />
      <Route path="history" element={<Dashboard view="history" />} />
      <Route path="about" element={<Dashboard view="about" />} />
      <Route path="patients" element={<Dashboard view="patients" />} />
      {/* 3D Interpreter route */}
      <Route path="interpreter" element={<Dashboard view="interpreter" />} />
      <Route path="bridge" element={<Dashboard view="bridge" />} />
      <Route path="settings" element={<Dashboard view="settings" />} />
    </Routes>
  );
};

export default App;
