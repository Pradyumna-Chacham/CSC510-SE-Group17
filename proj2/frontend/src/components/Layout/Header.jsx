import React from 'react';
import { Link } from 'react-router-dom';
import useSessionStore from '../../store/useSessionStore';

function Header() {
  const { currentSessionId } = useSessionStore();

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <span className="text-2xl font-bold text-primary">📋 ReqEngine</span>
          </Link>

          {/* Session Info */}
          <div className="flex items-center gap-4">
            {currentSessionId && (
              <div className="text-sm">
                <span className="text-gray-500">Session:</span>{' '}
                <span className="font-mono text-primary">
                  {currentSessionId.substring(0, 8)}...
                </span>
              </div>
            )}
            
            <Link
              to="/extraction"
              className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
            >
              New Extraction
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;