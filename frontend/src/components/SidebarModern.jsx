import React from 'react';
import { LayoutDashboard, Users, FileCheck, BarChart3, Settings, ChevronRight, Clipboard, BookOpen, Shield } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

const Sidebar = () => {
  const location = useLocation();
  const { user } = useAuth();

  const navigationItems = [
    {
      icon: LayoutDashboard,
      label: 'Dashboard',
      href: '/dashboard',
      badge: null,
      roles: ['admin', 'administ'],
    },
    {
      icon: Users,
      label: 'Postulantes',
      href: '/postulantes',
      badge: null,
      roles: ['admin', 'administ', 'estudiante'],
    },
    {
      icon: Clipboard,
      label: 'Postulaciones',
      href: '/postulaciones',
      badge: null,
      roles: ['admin', 'administ', 'estudiante'],
    },
    {
      icon: FileCheck,
      label: 'Documentos',
      href: '/documentos',
      badge: 12,
      roles: ['admin', 'administ', 'estudiante'],
    },
    {
      icon: BookOpen,
      label: 'Modalidades',
      href: '/modalidades',
      badge: null,
      roles: ['admin', 'administ'],
    },
    {
      icon: Shield,
      label: 'Usuarios',
      href: '/usuarios',
      badge: null,
      roles: ['admin'],
    },
    {
      icon: BarChart3,
      label: 'Reportes',
      href: '/reportes',
      badge: null,
      roles: ['admin', 'administ'],
    },
  ];

  const resolveRole = () => {
    if (user?.role) return user.role;
    if (user?.is_superuser === true) return 'admin';
    return null;
  };

  const basicMenuHrefs = new Set([
    '/dashboard',
    '/postulantes',
    '/postulaciones',
    '/documentos',
  ]);

  const effectiveRole = resolveRole();

  const visibleItems = effectiveRole
    ? navigationItems.filter((item) => item.roles.includes(effectiveRole))
    : navigationItems.filter((item) => basicMenuHrefs.has(item.href));

  const isActive = (href) => location.pathname === href || location.pathname.startsWith(href + '/');

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 z-50 flex flex-col">
      {/* Bloque Superior - Logo + Navegación + Configuración */}
      <div className="space-y-6">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <LayoutDashboard className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">Graduación</h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">Sistema de Gestión</p>
            </div>
          </div>
        </div>

        {/* Navegación + Separador + Configuración */}
        <div>
          {/* Navegación */}
          <nav className="px-4 pb-4 space-y-2">
            {visibleItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);

              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={`flex items-center justify-between px-4 py-3 rounded-lg transition-all duration-200 ease-in-out group ${
                    active
                      ? 'bg-blue-500 text-white shadow-md shadow-blue-500/40'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      active
                        ? 'bg-white/20 text-white'
                        : 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                  {active && <ChevronRight className="w-5 h-5 opacity-0 group-hover:opacity-100 transition-all duration-200" />}
                </Link>
              );
            })}
          </nav>

          {/* Separador */}
          <div className="mx-4 my-4 border-t border-gray-200 dark:border-gray-800"></div>

          {/* Configuración */}
          <nav className="px-4 space-y-2">
            <Link
              to="/configuracion"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ease-in-out group ${
                isActive('/configuracion')
                  ? 'bg-blue-500 text-white shadow-md shadow-blue-500/40'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50'
              }`}
            >
              <Settings className="w-5 h-5" />
              <span className="font-medium">Configuración</span>
            </Link>
          </nav>
        </div>
      </div>

      {/* Footer Info */}
      <div className="mt-8 p-4 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-4">
          <p className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-2">
            ¿Necesitas ayuda?
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
            Consulta nuestra documentación o contacta al equipo de soporte.
          </p>
          <button className="w-full px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white text-xs font-semibold rounded-lg transition-colors">
            Contactar Soporte
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
