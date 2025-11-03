import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../../api/client';
import useSessionStore from '../../store/useSessionStore';
import { formatDate } from '../../utils/formatters';

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentSessionId, setCurrentSession } = useSessionStore();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await api.getSessions();
      setSessions(response.data.sessions);
    } catch (error) {
      console.log('Sessions not loaded');
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setCurrentSession(null);
    navigate('/');
  };

  const handleSelectSession = (sessionId) => {
    setCurrentSession(sessionId);
    navigate('/');
  };

  const handleDeleteSession = async (sessionId, e) => {
    e.stopPropagation(); // Prevent session selection
    
    if (!window.confirm('Delete this session?')) return;

    try {
      await api.deleteSession(sessionId);
      setSessions(sessions.filter(s => s.session_id !== sessionId));
      if (currentSessionId === sessionId) {
        setCurrentSession(null);
      }
    } catch (error) {
      console.log('Delete failed');
    }
  };

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col h-screen">
      {/* New Chat Button */}
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 bg-gray-800 hover:bg-gray-700 px-4 py-3 rounded-lg transition font-medium"
        >
          <span className="text-xl">+</span>
          <span>New Chat</span>
        </button>
      </div>

      {/* Session History */}
      <div className="flex-1 overflow-y-auto p-2">
        <div className="text-xs text-gray-400 px-3 py-2 font-semibold uppercase">
          Recent Sessions
        </div>
        
        {loading ? (
          <div className="px-3 py-2 text-sm text-gray-400">Loading...</div>
        ) : sessions.length === 0 ? (
          <div className="px-3 py-2 text-sm text-gray-400">No sessions yet</div>
        ) : (
          <div className="space-y-1">
            {sessions.map((session) => (
              <div
                key={session.session_id}
                onClick={() => handleSelectSession(session.session_id)}
                className={`group relative px-3 py-2 rounded-lg cursor-pointer transition ${
                  currentSessionId === session.session_id
                    ? 'bg-gray-700'
                    : 'hover:bg-gray-800'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {session.project_context || 'Untitled Session'}
                    </p>
                    <p className="text-xs text-gray-400 truncate">
                      {session.domain || 'No domain'}
                    </p>
                  </div>
                  
                  {/* Delete Button - Shows on hover */}
                  <button
                    onClick={(e) => handleDeleteSession(session.session_id, e)}
                    className="opacity-0 group-hover:opacity-100 ml-2 p-1 hover:bg-red-600 rounded transition"
                    title="Delete session"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <p className="text-xs text-gray-500 mt-1">
                  {formatDate(session.last_active)}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Bottom Info */}
      <div className="p-4 border-t border-gray-700">
        <div className="text-xs text-gray-400">
          {currentSessionId && (
            <div className="mb-2">
              <span className="text-gray-500">Active: </span>
              <span className="font-mono">{currentSessionId.substring(0, 8)}...</span>
            </div>
          )}
          <div className="text-gray-500">ReqEngine v1.0</div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;