/**
 * Admin Layout Component
 * Wraps protected pages with Header and Sidebar
 * Includes global loader for HTTP requests
 * Includes global notification system (react-hot-toast)
 */

import { Toaster } from 'react-hot-toast';
import Header from '../components/Header';
import SidebarModern from '../components/SidebarModern';
import GlobalLoader from '../components/ui/GlobalLoader';

const AdminLayout = ({ children }) => {
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Global Loader */}
      <GlobalLoader />

      {/* Global Notifications */}
      <Toaster
        position="top-right"
        reverseOrder={false}
        gutter={8}
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#333',
          },
        }}
      />
      
      {/* Header */}
      <Header />

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <SidebarModern />

        {/* Content Area - ml-64 offsets the fixed sidebar (w-64) */}
        <main className="flex-1 overflow-auto ml-64 transition-all duration-200 ease-in-out">
          <div className="px-4 py-6 max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
