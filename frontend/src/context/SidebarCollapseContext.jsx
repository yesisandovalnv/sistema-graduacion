import React, { createContext, useContext, useState } from 'react';

const SidebarCollapseContext = createContext();

export const SidebarCollapseProvider = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <SidebarCollapseContext.Provider value={{ collapsed, setCollapsed }}>
      {children}
    </SidebarCollapseContext.Provider>
  );
};

export const useSidebarCollapse = () => {
  const context = useContext(SidebarCollapseContext);
  if (!context) {
    throw new Error('useSidebarCollapse must be used within SidebarCollapseProvider');
  }
  return context;
};
