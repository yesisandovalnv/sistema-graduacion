import React from 'react';
import { TrendingUp, TrendingDown, Users, FileText, CheckCircle, Zap } from 'lucide-react';

const StatsCards = ({ stats = {} }) => {
  const defaultStats = {
    totalPostulantes: { value: 248, change: 12, icon: Users, color: 'blue' },
    documentosPendientes: { value: 42, change: -8, icon: FileText, color: 'yellow' },
    graduados: { value: 156, change: 24, icon: CheckCircle, color: 'green' },
    tasaAprobacion: { value: 87, change: 5, icon: Zap, color: 'purple' },
  };

  // Merge profundo: preserva iconos del default si no están en stats
  const data = Object.keys(defaultStats).reduce((acc, key) => {
    acc[key] = { ...defaultStats[key], ...(stats[key] || {}) };
    return acc;
  }, {});

  const getColorClasses = (color) => {
    const colors = {
      blue: 'from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700',
      yellow: 'from-yellow-500 to-orange-600 dark:from-yellow-600 dark:to-orange-700',
      green: 'from-green-500 to-emerald-600 dark:from-green-600 dark:to-emerald-700',
      purple: 'from-purple-500 to-pink-600 dark:from-purple-600 dark:to-pink-700',
    };
    return colors[color] || colors.blue;
  };

  const getIconBgColor = (color) => {
    const colors = {
      blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
      yellow: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400',
      green: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
      purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
    };
    return colors[color] || colors.blue;
  };

  const StatCard = ({ title, value, change, Icon, colorClass, bgColorClass }) => {
    const isPositive = change >= 0;

    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-slate-700/50 hover:shadow-lg hover:-translate-y-1 hover:shadow-xl transition-all duration-300 overflow-hidden group">
        {/* Borde superior degradado */}
        <div className={`h-1 bg-gradient-to-r ${colorClass}`}></div>

        <div className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                {title}
              </p>
              <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                {typeof value === 'number' && value > 100 ? value : value}
                {title.includes('Tasa') ? '%' : ''}
              </h3>

              {/* Cambio */}
              <div className="flex items-center gap-2">
                {isPositive ? (
                  <TrendingUp className="w-4 h-4 text-green-500" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-500" />
                )}
                <span className={`text-sm font-semibold ${
                  isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                }`}>
                  {isPositive ? '+' : ''}{change}%
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">vs mes anterior</span>
              </div>
            </div>

            {/* Icono */}
            <div className={`${bgColorClass} p-3 rounded-lg group-hover:scale-110 transition-transform`}>
              <Icon className="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
      <StatCard
        title="Total Postulantes"
        value={data.totalPostulantes.value}
        change={data.totalPostulantes.change}
        Icon={data.totalPostulantes.icon}
        colorClass={getColorClasses(data.totalPostulantes.color)}
        bgColorClass={getIconBgColor(data.totalPostulantes.color)}
      />
      <StatCard
        title="Documentos Pendientes"
        value={data.documentosPendientes.value}
        change={data.documentosPendientes.change}
        Icon={data.documentosPendientes.icon}
        colorClass={getColorClasses(data.documentosPendientes.color)}
        bgColorClass={getIconBgColor(data.documentosPendientes.color)}
      />
      <StatCard
        title="Graduados"
        value={data.graduados.value}
        change={data.graduados.change}
        Icon={data.graduados.icon}
        colorClass={getColorClasses(data.graduados.color)}
        bgColorClass={getIconBgColor(data.graduados.color)}
      />
      <StatCard
        title="Tasa de Aprobación"
        value={data.tasaAprobacion.value}
        change={data.tasaAprobacion.change}
        Icon={data.tasaAprobacion.icon}
        colorClass={getColorClasses(data.tasaAprobacion.color)}
        bgColorClass={getIconBgColor(data.tasaAprobacion.color)}
      />
    </div>
  );
};

export default StatsCards;
