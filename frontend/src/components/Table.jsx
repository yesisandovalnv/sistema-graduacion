/**
 * Table Component
 * Tabla genérica reutilizable con acciones
 */

import React from 'react';

const Table = ({ columns, data, loading, onEdit, onDelete, onView }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-gray-500 font-medium">No hay datos disponibles</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto bg-white rounded-lg shadow">
      <table className="w-full">
        <thead className="bg-gray-100 border-b">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className={`px-6 py-3 text-left text-sm font-semibold text-gray-700 ${
                  col.width ? `w-${col.width}` : ''
                }`}
              >
                {col.label}
              </th>
            ))}
            {(onEdit || onDelete || onView) && (
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                Acciones
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={row.id || idx} className="border-b hover:bg-gray-50 transition">
              {columns.map((col) => (
                <td key={`${row.id}-${col.key}`} className="px-6 py-4 text-sm text-gray-800">
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
              {(onEdit || onDelete || onView) && (
                <td className="px-6 py-4 text-sm">
                  <div className="flex gap-2">
                    {onView && (
                      <button
                        onClick={() => onView(row)}
                        className="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition text-xs font-medium"
                        title="Ver"
                      >
                        👁️
                      </button>
                    )}
                    {onEdit && (
                      <button
                        onClick={() => onEdit(row)}
                        className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition text-xs font-medium"
                        title="Editar"
                      >
                        ✏️
                      </button>
                    )}
                    {onDelete && (
                      <button
                        onClick={() => {
                          if (window.confirm('¿Estás seguro de que deseas eliminar?')) {
                            onDelete(row);
                          }
                        }}
                        className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition text-xs font-medium"
                        title="Eliminar"
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Table;
