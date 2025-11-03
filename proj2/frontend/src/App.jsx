import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Layout
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';

// Pages
import Dashboard from './pages/Dashboard';
import Extraction from './pages/Extraction';
import UseCaseDetail from './pages/UseCaseDetail';
import SessionHistory from './pages/SessionHistory';
import Analytics from './pages/Analytics';
import Query from './pages/Query';
import Export from './pages/Export';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        
        <div className="flex">
          <Sidebar />
          
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/extraction" element={<Extraction />} />
              <Route path="/use-case/:id" element={<UseCaseDetail />} />
              <Route path="/sessions" element={<SessionHistory />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/query" element={<Query />} />
              <Route path="/export" element={<Export />} />
            </Routes>
          </main>
        </div>

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