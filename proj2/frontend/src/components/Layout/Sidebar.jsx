import React, { useEffect, useState, useRef } from 'react';
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
const [isCollapsed, setIsCollapsed] = useState(false);
const [sidebarWidth, setSidebarWidth] = useState(256); // 256px = w-64
const [isResizing, setIsResizing] = useState(false);

const sidebarRef = useRef(null);
const minWidth = 200;
const maxWidth = 500;

useEffect(() => {
loadSessions();
}, []);

useEffect(() => {
if (isResizing) {
const handleMouseMove = (e) => {
const newWidth = e.clientX;
if (newWidth >= minWidth && newWidth <= maxWidth) {
setSidebarWidth(newWidth);
}
};


  const handleMouseUp = () => {  
    setIsResizing(false);  
  };  

  document.addEventListener('mousemove', handleMouseMove);  
  document.addEventListener('mouseup', handleMouseUp);  

  return () => {  
    document.removeEventListener('mousemove', handleMouseMove);  
    document.removeEventListener('mouseup', handleMouseUp);  
  };  
}  


}, [isResizing]);

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
e.stopPropagation();


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

const startResizing = () => {
setIsResizing(true);
};

return (
<>
<aside
ref={sidebarRef}
style={{ width: isCollapsed ? '60px' : `${sidebarWidth}px` }}
className="bg-gray-900 text-white flex flex-col h-screen relative transition-all duration-300"
>
{/* Collapse/Expand Button */} <div className="absolute -right-3 top-6 z-10">
<button
onClick={() => setIsCollapsed(!isCollapsed)}
className="bg-gray-700 hover:bg-gray-600 rounded-full p-1.5 shadow-lg transition"
title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
>
<svg
className={`w-4 h-4 transition-transform ${isCollapsed ? 'rotate-180' : ''}`}
fill="none"
stroke="currentColor"
viewBox="0 0 24 24"
> <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /> </svg> </button> </div>

```
    {/* New Chat Button */}  
    <div className="p-4 border-b border-gray-700">  
      <button  
        onClick={handleNewChat}  
        className="w-full flex items-center justify-center gap-2 bg-gray-800 hover:bg-gray-700 px-4 py-3 rounded-lg transition font-medium"  
        title="New Chat"  
      >  
        <span className="text-xl">+</span>  
        {!isCollapsed && <span>New Chat</span>}  
      </button>  
    </div>  

    {/* Session History */}  
    {!isCollapsed && (  
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
                      {session.session_title || session.project_context || 'Untitled Session'}  
                    </p>  
                  </div>  

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
    )}  

    {/* Bottom Info */}  
    {!isCollapsed && (  
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
    )}  

    {/* Resize Handle */}  
    {!isCollapsed && (  
      <div  
        onMouseDown={startResizing}  
        className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-blue-500 transition-colors"  
        style={{ userSelect: 'none' }}  
      />  
    )}  
  </aside>  

  {/* Overlay during resizing */}  
  {isResizing && (  
    <div className="fixed inset-0 z-50 cursor-col-resize" style={{ userSelect: 'none' }} />  
  )}  
</>  


);
}

export default Sidebar;
