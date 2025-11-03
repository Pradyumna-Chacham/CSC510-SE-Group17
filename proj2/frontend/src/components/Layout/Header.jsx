import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Header() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Chat', icon: '💬' },
    { path: '/analytics', label: 'Analytics', icon: '📊' },
    { path: '/export', label: 'Export', icon: '📥' },
    { path: '/query', label: 'Query', icon: '🔍' },
  ];

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3">
          <span className="text-2xl">📋</span>
          <span className="text-xl font-bold text-gray-900">ReqEngine</span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                location.pathname === item.path
                  ? 'bg-indigo-100 text-indigo-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <span>{item.icon}</span>
              <span className="text-sm">{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

export default Header;