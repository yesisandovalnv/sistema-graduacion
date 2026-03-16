/**
 * Reportes Page - Modern Dashboard
 * Analytics and reports with modern UI
 */

import { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import api from '../api/api';
import { API_CONFIG } from '../constants/api';
import { AlertCircle, Download } from 'lucide-react';

const Reportes = () => {
  const { isDark } = useTheme();
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('general');
  const [exportingTutores, setExportingTutores] = useState(false);

  useEffect(() => {
    fetchReportData();
  }, [activeTab]);

  const fetchReportData = async () => {
    try {
      setLoading(true);
      setError('');
      
      let endpoint = API_CONFIG.ENDPOINTS.DASHBOARD_GENERAL;

      if (activeTab === 'tutores') {
        endpoint = API_CONFIG.ENDPOINTS.ESTADISTICAS_TUTORES;
      } else if (activeTab === 'carreras') {
        endpoint = API_CONFIG.ENDPOINTS.EFICIENCIA_CARRERAS;
      }

      const result = await api.getAll(endpoint);

      if (result.success) {
        setReportData(result.data);
      } else {
        throw new Error(result.error || 'Error al cargar reportes');
      }
    } catch (err) {
      console.error('Error loading reports:', err);
      setError(err.message || 'Error al cargar los reportes');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      setExportingTutores(true);
      const response = await api.axiosInstance.get(
        API_CONFIG.ENDPOINTS.EXPORTAR_ESTADISTICAS,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `estadisticas_tutores_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
      setError('Error al exportar estadísticas');
    } finally {
      setExportingTutores(false);
    }
  };

  const renderGeneralStats = () => {
    if (!reportData) return null;

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Postulantes */}
        <div className={`p-6 rounded-xl border dark:border-gray-700 ${
          isDark ? 'bg-gray-800' : 'bg-white'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                Total Postulantes
              </p>
              <p className={`text-3xl font-bold mt-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {reportData.total_postulantes || 0}
              </p>
            </div>
            <div className="text-4xl">👥</div>
          </div>
        </div>

        {/* Total Postulaciones */}
        <div className={`p-6 rounded-xl border dark:border-gray-700 ${
          isDark ? 'bg-gray-800' : 'bg-white'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                Total Postulaciones
              </p>
              <p className={`text-3xl font-bold mt-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {reportData.total_postulaciones || 0}
              </p>
            </div>
            <div className="text-4xl">📋</div>
          </div>
        </div>

        {/* Documentos Pendientes */}
        <div className={`p-6 rounded-xl border dark:border-gray-700 ${
          isDark ? 'bg-gray-800' : 'bg-white'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                Documentos Pendientes
              </p>
              <p className={`text-3xl font-bold mt-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {reportData.documentos_pendientes || 0}
              </p>
            </div>
            <div className="text-4xl">⏳</div>
          </div>
        </div>

        {/* Total Titulados */}
        <div className={`p-6 rounded-xl border dark:border-gray-700 ${
          isDark ? 'bg-gray-800' : 'bg-white'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                Total Titulados
              </p>
              <p className={`text-3xl font-bold mt-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {reportData.total_titulados || 0}
              </p>
            </div>
            <div className="text-4xl">🏆</div>
          </div>
        </div>
      </div>
    );
  };

  const renderByEstado = () => {
    if (!reportData?.postulaciones_por_estado_general) return null;

    return (
      <div className={`p-6 rounded-xl border dark:border-gray-700 ${
        isDark ? 'bg-gray-800' : 'bg-white'
      }`}>
        <h3 className={`text-lg font-semibold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
          Postulaciones por Estado
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {reportData.postulaciones_por_estado_general.map((item, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-lg border dark:border-gray-700 ${
                isDark ? 'bg-gray-700' : 'bg-gray-50'
              }`}
            >
              <p className={`text-xs font-medium uppercase ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                {item.estado}
              </p>
              <p className={`text-2xl font-bold mt-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {item.total}
              </p>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderTutoresStats = () => {
    if (!reportData?.results) return null;

    return (
      <div className={`p-6 rounded-xl border dark:border-gray-700 ${
        isDark ? 'bg-gray-800' : 'bg-white'
      }`}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className={`border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
              <tr>
                <th className={`text-left py-3 px-4 font-semibold ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  Tutor
                </th>
                <th className={`text-center py-3 px-4 font-semibold ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  Aprobados
                </th>
                <th className={`text-center py-3 px-4 font-semibold ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  Rechazados
                </th>
                <th className={`text-center py-3 px-4 font-semibold ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  Total
                </th>
                <th className={`text-right py-3 px-4 font-semibold ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  % Aprobación
                </th>
              </tr>
            </thead>
            <tbody>
              {reportData.results.map((tutor, idx) => (
                <tr
                  key={idx}
                  className={`border-b ${isDark ? 'border-gray-700' : 'border-gray-100'} hover:${isDark ? 'bg-gray-700' : 'bg-gray-50'}`}
                >
                  <td className={`py-3 px-4 ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>
                    {tutor.tutor_nombre || 'Sin datos'}
                  </td>
                  <td className={`py-3 px-4 text-center font-medium text-green-600 dark:text-green-400`}>
                    {tutor.aprobados || 0}
                  </td>
                  <td className={`py-3 px-4 text-center font-medium text-red-600 dark:text-red-400`}>
                    {tutor.rechazados || 0}
                  </td>
                  <td className={`py-3 px-4 text-center font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    {(tutor.aprobados || 0) + (tutor.rechazados || 0)}
                  </td>
                  <td className={`py-3 px-4 text-right font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    {tutor.total_procesados > 0
                      ? ((tutor.aprobados / tutor.total_procesados) * 100).toFixed(1)
                      : 0}
                    %
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Encabezado */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Reportes y Análisis
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Visualiza estadísticas y análisis del sistema
          </p>
        </div>

        {/* Tabs */}
        <div className={`mb-6 flex flex-wrap gap-2 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          {[
            { id: 'general', label: 'General', icon: '📊' },
            { id: 'tutores', label: 'Tutores', icon: '👨‍🏫' },
            { id: 'carreras', label: 'Carreras', icon: '🎓' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 font-medium transition border-b-2 flex items-center gap-2 ${
                activeTab === tab.id
                  ? `border-blue-600 text-blue-600 ${isDark ? 'text-blue-400' : ''}`
                  : `border-transparent ${isDark ? 'text-gray-400 hover:text-gray-300' : 'text-gray-600 hover:text-gray-800'}`
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* Error Alert */}
        {error && (
          <div className={`mb-6 p-4 rounded-lg border flex items-start gap-3 ${
            isDark
              ? 'bg-red-900/20 border-red-800 text-red-400'
              : 'bg-red-50 border-red-200 text-red-800'
          }`}>
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Error al cargar reportes</p>
              <p className="text-sm mt-1">{error}</p>
              <button
                onClick={fetchReportData}
                className="text-sm mt-2 underline hover:no-underline"
              >
                Reintentar
              </button>
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-500 dark:text-gray-400">Cargando datos...</p>
            </div>
          </div>
        )}

        {/* Content */}
        {!loading && !error && (
          <>
            {activeTab === 'general' && renderGeneralStats()}
            {activeTab === 'general' && reportData && renderByEstado()}

            {activeTab === 'tutores' && (
              <div className="flex justify-end mb-4">
                <button
                  onClick={handleExport}
                  disabled={exportingTutores}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded-lg transition font-medium"
                >
                  <Download className="w-4 h-4" />
                  {exportingTutores ? 'Exportando...' : 'Exportar Excel'}
                </button>
              </div>
            )}
            {activeTab === 'tutores' && renderTutoresStats()}

            {activeTab === 'carreras' && reportData && (
              <div className={`p-6 rounded-xl border dark:border-gray-700 ${
                isDark ? 'bg-gray-800' : 'bg-white'
              }`}>
                <h3 className={`text-lg font-semibold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  Eficiencia por Carrera
                </h3>
                <p className={isDark ? 'text-gray-400' : 'text-gray-600'}>
                  Datos de eficiencia por carrera: {JSON.stringify(reportData).substring(0, 100)}...
                </p>
              </div>
            )}

            {/* Footer */}
            <div className={`mt-8 p-4 rounded-lg border text-sm ${
              isDark
                ? 'bg-gray-900 border-gray-700 text-gray-400'
                : 'bg-gray-50 border-gray-200 text-gray-600'
            }`}>
              <p>ℹ️ Última actualización: {new Date().toLocaleString('es-ES')}</p>
            </div>
          </>
        )}
    </div>
  );
};

export default Reportes;
