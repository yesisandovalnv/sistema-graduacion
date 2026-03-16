import React from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const Charts = ({ isDark = false }) => {
  // Datos para el gráfico de barras (Postulantes por semana)
  const barChartData = [
    { semana: 'Sem 1', postulantes: 45, documentos: 38 },
    { semana: 'Sem 2', postulantes: 52, documentos: 48 },
    { semana: 'Sem 3', postulantes: 38, documentos: 35 },
    { semana: 'Sem 4', postulantes: 61, documentos: 55 },
    { semana: 'Sem 5', postulantes: 58, documentos: 52 },
    { semana: 'Sem 6', postulantes: 72, documentos: 68 },
  ];

  // Datos para el gráfico de línea (Progreso en el tiempo)
  const lineChartData = [
    { mes: 'Ene', graduados: 45, pendientes: 120, aprobados: 95 },
    { mes: 'Feb', graduados: 72, pendientes: 98, aprobados: 142 },
    { mes: 'Mar', graduados: 98, pendientes: 76, aprobados: 165 },
    { mes: 'Abr', graduados: 125, pendientes: 62, aprobados: 189 },
    { mes: 'May', graduados: 145, pendientes: 48, aprobados: 210 },
    { mes: 'Jun', graduados: 156, pendientes: 42, aprobados: 248 },
  ];

  // Datos para el gráfico circular (Distribución por estado)
  const pieChartData = [
    { name: 'Completado', value: 45, color: '#10b981' },
    { name: 'En Proceso', value: 30, color: '#f59e0b' },
    { name: 'Por Revisar', value: 15, color: '#3b82f6' },
    { name: 'Rechazado', value: 10, color: '#ef4444' },
  ];

  const chartColors = {
    textColor: isDark ? '#e5e7eb' : '#374151',
    gridColor: isDark ? '#374151' : '#e5e7eb',
    barColor1: '#3b82f6',
    barColor2: '#8b5cf6',
    lineColor1: '#10b981',
    lineColor2: '#f59e0b',
    lineColor3: '#ef4444',
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
      {/* Gráfico de Barras */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 h-[320px] hover:shadow-xl transition-all duration-300">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Postulantes & Documentos por Semana
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke={chartColors.gridColor} />
            <XAxis dataKey="semana" stroke={chartColors.textColor} style={{ fontSize: '12px' }} />
            <YAxis stroke={chartColors.textColor} style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#1f2937' : '#ffffff',
                border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                borderRadius: '8px',
                color: chartColors.textColor,
              }}
              cursor={{ fill: isDark ? 'rgba(59, 130, 246, 0.1)' : 'rgba(59, 130, 246, 0.1)' }}
            />
            <Legend wrapperStyle={{ paddingTop: '16px' }} />
            <Bar dataKey="postulantes" fill={chartColors.barColor1} radius={[8, 8, 0, 0]} />
            <Bar dataKey="documentos" fill={chartColors.barColor2} radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Gráfico de Línea */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 h-[320px] hover:shadow-xl transition-all duration-300">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Progreso General (6 Meses)
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={lineChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke={chartColors.gridColor} />
            <XAxis dataKey="mes" stroke={chartColors.textColor} style={{ fontSize: '12px' }} />
            <YAxis stroke={chartColors.textColor} style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#1f2937' : '#ffffff',
                border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                borderRadius: '8px',
                color: chartColors.textColor,
              }}
              cursor={{ stroke: isDark ? 'rgba(59, 130, 246, 0.2)' : 'rgba(59, 130, 246, 0.2)' }}
            />
            <Legend wrapperStyle={{ paddingTop: '16px' }} />
            <Line
              type="monotone"
              dataKey="graduados"
              stroke={chartColors.lineColor1}
              strokeWidth={3}
              dot={{ fill: chartColors.lineColor1, r: 4 }}
              activeDot={{ r: 6 }}
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="aprobados"
              stroke={chartColors.lineColor2}
              strokeWidth={3}
              dot={{ fill: chartColors.lineColor2, r: 4 }}
              activeDot={{ r: 6 }}
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="pendientes"
              stroke={chartColors.lineColor3}
              strokeWidth={3}
              dot={{ fill: chartColors.lineColor3, r: 4 }}
              activeDot={{ r: 6 }}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Gráfico Circular - Primera mitad (ancho completo en móvil, mitad en desktop) */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 lg:col-span-1 h-[320px] hover:shadow-xl transition-all duration-300">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Distribución por Estado
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieChartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {pieChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#1f2937' : '#ffffff',
                border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                borderRadius: '8px',
                color: chartColors.textColor,
              }}
            />
          </PieChart>
        </ResponsiveContainer>

        {/* Leyenda personalizada */}
        <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
          {pieChartData.map((item, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: item.color }}
              ></div>
              <span className="text-gray-600 dark:text-gray-400">
                {item.name}: {item.value}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Resumen de Métricas Clave */}
      <div className="bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 h-[320px] hover:shadow-xl transition-all duration-300">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Resumen de Métricas
        </h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <span className="text-gray-600 dark:text-gray-400">Tasa Completación</span>
            <span className="text-lg font-semibold text-green-600 dark:text-green-400">87%</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <span className="text-gray-600 dark:text-gray-400">Promedio Procesamiento</span>
            <span className="text-lg font-semibold text-blue-600 dark:text-blue-400">4.2 días</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <span className="text-gray-600 dark:text-gray-400">Satisfacción</span>
            <span className="text-lg font-semibold text-purple-600 dark:text-purple-400">9.1/10</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <span className="text-gray-600 dark:text-gray-400">Proyección Mes</span>
            <span className="text-lg font-semibold text-orange-600 dark:text-orange-400">+24%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Charts;
