import React from 'react'

function HistorialAuditoria({ items = [], tiposDocumento = [] }) {
  const getTipoDocumentoNombre = (tipoId) => {
    const tipo = tiposDocumento.find((t) => t.id === tipoId)
    return tipo ? tipo.nombre : `ID ${tipoId}`
  }

  const formatMessage = (item) => {
    switch (item.accion) {
      case 'CAMBIO_ETAPA':
        return `avanzó la etapa de "${item.estado_anterior?.etapa_nombre || 'Ninguna'}" a "${item.estado_nuevo?.etapa_nombre}".`
      case 'APROBACION_DOCUMENTO':
      case 'RECHAZO_DOCUMENTO':
        const nombreDoc = getTipoDocumentoNombre(item.detalles?.tipo_documento_id)
        const accion = item.accion === 'APROBACION_DOCUMENTO' ? 'aprobó' : 'rechazó'
        const url = item.documento_url
        
        return (
          <span>
            {accion} el documento{' '}
            {url ? (
              <a href={url} target="_blank" rel="noopener noreferrer" style={{ color: '#0284c7', textDecoration: 'underline' }}>
                "{nombreDoc}"
              </a>
            ) : (
              `"${nombreDoc}"`
            )}.
          </span>
        )
      default:
        return `realizó la acción: ${item.accion}`
    }
  }

  if (!items.length) {
    return <p style={{ color: '#64748b', textAlign: 'center', padding: '1rem 0' }}>No hay historial de eventos.</p>
  }

  return (
    <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {items.map((item) => (
        <li key={item.id} style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '1rem' }}>
          <div style={{ flexShrink: 0, width: '2.5rem', height: '2.5rem', borderRadius: '9999px', backgroundColor: '#e0f2fe', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0c4a6e', fontWeight: '600' }}>
            {item.usuario?.username.substring(0, 2).toUpperCase() || 'S'}
          </div>
          <div>
            <p style={{ margin: 0, fontWeight: '500' }}>
              <span style={{ fontWeight: '600' }}>{item.usuario?.username || 'Sistema'}</span> {formatMessage(item)}
            </p>
            <p style={{ margin: '0.25rem 0 0', fontSize: '0.875rem', color: '#64748b' }}>
              {new Date(item.fecha).toLocaleString()}
            </p>
          </div>
        </li>
      ))}
    </ul>
  )
}

export default HistorialAuditoria