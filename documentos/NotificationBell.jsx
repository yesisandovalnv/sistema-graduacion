import { useEffect, useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { fetchList, createItem } from '../api/endpoints'
import { useAuth } from '../context/AuthContext'

function NotificationBell() {
  const { isAuthenticated } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef(null)
  const buttonRef = useRef(null)
  const panelRef = useRef(null)

  const unreadCount = notifications.filter((n) => !n.leida).length

  const loadNotifications = async () => {
    if (!isAuthenticated) return
    try {
      const { items } = await fetchList('/notificaciones/')
      setNotifications(items)
    } catch (error) {
      console.error('Failed to fetch notifications', error)
    }
  }

  useEffect(() => {
    loadNotifications()
    const interval = setInterval(loadNotifications, 60000) // Actualiza cada minuto
    return () => clearInterval(interval)
  }, [isAuthenticated])

  useEffect(() => {
    const handleClickOutside = (event) => {
      // Si hace clic en el botón, ignorar (handleToggle lo maneja)
      if (buttonRef.current && buttonRef.current.contains(event.target)) {
        return
      }
      
      // Si hace clic dentro del panel, no cerrar
      if (panelRef.current && panelRef.current.contains(event.target)) {
        return
      }
      
      // Si hace clic fuera del botón Y del panel, cerrar
      setIsOpen(false)
    }
    
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleToggle = async () => {
    const nextState = !isOpen
    setIsOpen(nextState)
    if (nextState && unreadCount > 0) {
      // Marca todas como leídas al abrir
      const unreadIds = notifications.filter((n) => !n.leida).map((n) => n.id)
      try {
        await Promise.all(unreadIds.map((id) => createItem(`/notificaciones/${id}/marcar_leida/`, {})))
        setNotifications((prev) => prev.map((n) => ({ ...n, leida: true })))
      } catch (error) {
        console.error('Failed to mark notifications as read', error)
      }
    }
  }

  const handleMarkAllAsRead = async () => {
    if (unreadCount === 0) return
    try {
      // Llama al nuevo endpoint
      await createItem('/notificaciones/marcar-todas-leidas/', {})
      // Actualiza el estado local para reflejar el cambio inmediatamente
      setNotifications((prev) => prev.map((n) => ({ ...n, leida: true })))
    } catch (error) {
      console.error('Failed to mark all as read', error)
    }
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="relative" ref={containerRef}>
      <button 
        ref={buttonRef}
        onClick={handleToggle} 
        className="relative bg-transparent border-none cursor-pointer p-2"
      >
        <span aria-hidden="true" className="text-2xl">🔔</span>
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 bg-red-600 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center font-bold">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div 
          ref={panelRef}
          className="absolute top-full right-0 mt-2 w-80 bg-white border border-slate-200 rounded-lg shadow-lg z-10"
        >
          <div className="p-4 border-b border-slate-200">
            <h4 className="m-0 text-base font-semibold">Notificaciones</h4>
          </div>
          <ul className="list-none m-0 p-0 max-h-96 overflow-y-auto">
            {notifications.length > 0 ? (
              notifications.map((n) => (
                <li key={n.id} className="border-b border-slate-100 last:border-b-0">
                  <Link
                    to={n.link || '#'}
                    onClick={() => setIsOpen(false)}
                    className={`block p-3 hover:bg-slate-50 ${!n.link && 'pointer-events-none'}`}
                  >
                    <p className="m-0 text-sm text-slate-700">{n.mensaje}</p>
                    <p className="m-0 mt-1 text-xs text-slate-500">{new Date(n.fecha_creacion).toLocaleString()}</p>
                  </Link>
                </li>
              ))
            ) : (
              <li className="p-4 text-center text-slate-500">No hay notificaciones.</li>
            )}
          </ul>
          {unreadCount > 0 && (
            <div className="p-2 border-t border-slate-200 text-center">
              <button
                onClick={handleMarkAllAsRead}
                className="text-sm text-sky-600 hover:text-sky-800 bg-transparent border-none cursor-pointer w-full"
              >
                Marcar todas como leídas
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default NotificationBell