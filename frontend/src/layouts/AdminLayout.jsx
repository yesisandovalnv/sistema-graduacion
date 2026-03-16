/**
 * Admin Layout Component
 * Wraps protected pages with Header and Sidebar
 * Includes global loader for HTTP requests
 */

import Header from '../components/Header';
import SidebarModern from '../components/SidebarModern';
import GlobalLoader from '../components/ui/GlobalLoader';

const AdminLayout = ({ children }) => {
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Global Loader */}
      <GlobalLoader />
      
      {/* Header */}
      <Header />

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <SidebarModern />

        {/* Content Area */}
        <main className="flex-1 overflow-auto">
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
