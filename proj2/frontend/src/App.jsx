import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Layout
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';

// Pages
import Chat from './pages/Chat';
import Analytics from './pages/Analytics';
import Query from './pages/Query';
import Export from './pages/Export';

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        {/* Left Sidebar - Session History */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col">
          {/* Top Header */}
          <Header />

          {/* Page Content */}
          <main className="flex-1 overflow-hidden">
            <Routes>
              <Route path="/" element={<Chat />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/query" element={<Query />} />
              <Route path="/export" element={<Export />} />
            </Routes>
          </main>
        </div>

        {/* Toast Notifications */}
        <ToastContainer
          position="bottom-right"
          autoClose={3000}
          hideProgressBar={false}
          newestOnTop
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </div>
    </Router>
  );
}

export default App;