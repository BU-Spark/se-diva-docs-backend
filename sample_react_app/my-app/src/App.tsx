import React from 'react';
import { Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import ImportantContactsPage from './pages/ImportantContactsPage';

const App: React.FC = () => {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/important-contacts" element={<ImportantContactsPage />} />
      </Routes>
    </div>
  );
};

export default App;
