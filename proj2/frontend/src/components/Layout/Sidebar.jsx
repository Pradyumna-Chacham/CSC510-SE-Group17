import React from 'react';
import { NavLink } from 'react-router-dom';

function Sidebar() {
  const navItems = [
    { path: '/', label: '🏠 Dashboard', icon: '🏠' },
    { path: '/extraction', label: '✨ Extract Use Cases', icon: '✨' },
    { path: '/sessions', label: '📚 Sessions', icon: '📚' },
    { path: '/analytics', label: '📊 Analytics', icon: '📊' },
    { path: '/query', label: '💬 Query', icon: '💬' },
    { path: '/export', label: '📥 Export', icon: '📥' },
  ];

  return (
    <aside className="w-64 bg-white border-r min-h-screen">
      <nav className="p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                isActive
                  ? 'bg-primary text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            <span className="text-xl">{item.icon}</span>
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;