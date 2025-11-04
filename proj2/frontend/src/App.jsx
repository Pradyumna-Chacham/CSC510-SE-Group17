import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Layout Components
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';

// Pages
import Chat from './pages/Chat';
import Extraction from './pages/Extraction';
// ❌ REMOVED: import Analytics from './pages/Analytics';
import Export from './pages/Export';
import Query from './pages/Query';
import UseCaseDetail from './pages/UseCaseDetail';
import UseCaseRefine from './pages/UseCaseRefine';

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        {/* Sidebar */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <Header />

          {/* Page Content */}
          <main className="flex-1 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Chat />} />
              <Route path="/extraction" element={<Extraction />} />
              {/* ❌ REMOVED: <Route path="/analytics" element={<Analytics />} /> */}
              <Route path="/export" element={<Export />} />
              <Route path="/query" element={<Query />} />
              <Route path="/use-case/:id" element={<UseCaseDetail />} />
              <Route path="/use-case/:id/refine" element={<UseCaseRefine />} />
            </Routes>
          </main>
        </div>

        {/* Toast Notifications */}
        <ToastContainer
          position="top-right"
          autoClose={3000}
          hideProgressBar={false}
          newestOnTop={false}
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