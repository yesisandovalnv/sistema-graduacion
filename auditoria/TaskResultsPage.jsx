import { useEffect, useState } from 'react'
import { fetchList, createItem } from '../api/endpoints'
import { useAuth } from '../context/AuthContext'

function TaskResultsPage() {
  const { user } = useAuth()
  const [tasks, setTasks] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [count, setCount] = useState(0)
  const [statusFilter, setStatusFilter] = useState('')
  const [search, setSearch] = useState('')
  const [actionMessage, setActionMessage] = useState({ type: '', text: '' })
  const [retryingTaskId, setRetryingTaskId] = useState(null)
  const PAGE_SIZE = 20 // Coincide con la configuración de DRF en settings.py

  useEffect(() => {
    const loadTasks = async () => {
      setLoading(true)
      try {
        const params = { page }
        if (statusFilter) {
          params.status = statusFilter
        }
        if (search) {
          params.search = search
        }
        const { items, count: totalCount } = await fetchList('/task-results/', params)
        setTasks(items)
        setCount(totalCount)
      } catch (err) {
        setError('No se pudo cargar el historial de tareas. Asegúrate de tener permisos de administrador.')
      } finally {
        setLoading(false)
      }
    }

    let timeoutId

    if (user?.role === 'admin') {
      timeoutId = setTimeout(() => {
        loadTasks()
      }, 400)
    } else {
      setError('Acceso denegado. Esta página es solo para administradores.')
      setLoading(false)
    }
    return () => clearTimeout(timeoutId)
  }, [user, page, statusFilter, search])

  if (loading) {
    return <section className="page-block fade-in"><p>Cargando historial de tareas...</p></section>
  }

  if (error) {
    return <section className="page-block fade-in"><p className="error-text">{error}</p></section>
  }

  const totalPages = Math.ceil(count / PAGE_SIZE)

  const handleFilterChange = (e) => {
    setStatusFilter(e.target.value)
    setPage(1) // Reset to first page when filter changes
  }

  const handleSearchChange = (e) => {
    setSearch(e.target.value)
    setPage(1)
  }

  const handleRetry = async (taskId) => {
    setRetryingTaskId(taskId)
    setActionMessage({ type: '', text: '' })
    try {
      const response = await createItem(`/task-results/${taskId}/retry/`, {})
      setActionMessage({ type: 'success', text: response.status || 'Tarea encolada para reintento.' })
    } catch (err) {
      setActionMessage({ type: 'error', text: err.response?.data?.error || 'No se pudo reintentar la tarea.' })
    } finally {
      setRetryingTaskId(null)
    }
  }

  return (
    <section className="page-block fade-in">
      <header className="page-header">
        <h2>Historial de Tareas Asíncronas</h2>
        <p>Resultados de las tareas ejecutadas por Celery.</p>
      </header>

      {actionMessage.text && (
        <div className={`p-4 mb-4 rounded-md ${actionMessage.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {actionMessage.text}
        </div>
      )}

      <div className="panel">
        <div className="filter-bar" style={{ marginBottom: '1rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <label className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-600">Filtrar por estado:</span>
            <select value={statusFilter} onChange={handleFilterChange} className="rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500">
              <option value="">Todos</option>
              <option value="SUCCESS">Éxito</option>
              <option value="FAILURE">Fallo</option>
            </select>
          </label>

          <label className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-600">Buscar:</span>
            <input
              type="text"
              value={search}
              onChange={handleSearchChange}
              placeholder="Nombre de tarea..."
              className="rounded-md border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
            />
          </label>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID de Tarea</th>
                <th>Nombre</th>
                <th>Estado</th>
                <th>Fecha de Finalización</th>
                <th>Resultado / Error</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.task_id}>
                  <td className="font-mono text-xs">{task.task_id.substring(0, 12)}...</td>
                  <td>{task.task_name}</td>
                  <td>
                    <span
                      className={`status-chip ${
                        task.status === 'SUCCESS' ? 'aprobado' : task.status === 'FAILURE' ? 'rechazado' : ''
                      }`}
                    >
                      {task.status}
                    </span>
                  </td>
                  <td>{new Date(task.date_done).toLocaleString()}</td>
                  <td>
                    {task.status === 'FAILURE' ? (
                      <details>
                        <summary className="cursor-pointer text-red-600">Ver Traceback</summary>
                        <pre className="mt-2 p-2 bg-red-50 text-red-800 rounded text-xs overflow-auto">
                          {task.traceback}
                        </pre>
                      </details>
                    ) : (
                      <span className="text-slate-600">{task.result}</span>
                    )}
                  </td>
                  <td>
                    {task.status === 'FAILURE' && (
                      <button
                        onClick={() => handleRetry(task.task_id)}
                        disabled={retryingTaskId === task.task_id}
                        className="button-small"
                      >
                        {retryingTaskId === task.task_id ? 'Reintentando...' : 'Reintentar'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {!tasks.length && (
                <tr>
                  <td colSpan="6" className="text-center text-slate-500 py-4">
                    No hay resultados de tareas registrados.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="mt-4 flex justify-center items-center gap-4">
            <button
              onClick={() => setPage((p) => p - 1)}
              disabled={page === 1 || loading}
              className="button-secondary"
            >
              Anterior
            </button>
            <span className="text-sm text-slate-600">
              Página {page} de {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page === totalPages || loading}
              className="button-secondary"
            >
              Siguiente
            </button>
          </div>
        )}
      </div>
    </section>
  )
}

export default TaskResultsPage