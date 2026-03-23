import React from 'react';
import Sidebar from './SidebarModern';
import Header from './Header';
import { useTheme } from '../context/ThemeContext';

const Layout = ({ children, user, onLogout }) => {
  const { isDark } = useTheme();

  return (
    <div className={isDark ? 'dark' : ''}>
      <div className="min-h-screen bg-white dark:bg-gray-950">
        <Sidebar />
        <div className="ml-0 lg:ml-64 transition-all duration-300">
          <Header user={user} onLogout={onLogout} />
          <main className="p-4 md:p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
};

export default Layout;
