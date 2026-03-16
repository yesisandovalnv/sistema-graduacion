/**
 * Example Usage for Global Notification System
 * 
 * Import anywhere in your components:
 * 
 * import { success, error, info, loading, dismissAll } from '@/utils/notify';
 * 
 * SUCCESS NOTIFICATION:
 * ---
 * success('Operación completada exitosamente');
 * 
 * ERROR NOTIFICATION:
 * ---
 * error('Ocurrió un error durante la operación');
 * 
 * INFO NOTIFICATION:
 * ---
 * info('Esta es una notificación informativa');
 * 
 * LOADING NOTIFICATION:
 * ---
 * const loadingId = loading('Por favor espera...');
 * // Luego de completar:
 * updateToast(loadingId, {
 *   type: 'success',
 *   message: '¡Completado!',
 *   duration: 2000,
 * });
 * 
 * DISMISS ALL NOTIFICATIONS:
 * ---
 * dismissAll();
 * 
 * CUSTOM OPTIONS:
 * ---
 * success('Mensaje personalizado', {
 *   duration: 3000,
 *   icon: '✨',
 *   position: 'bottom-center',
 * });
 * 
 * USAGE IN COMPONENTS:
 * ---
 * import { useState } from 'react';
 * import { success, error } from '@/utils/notify';
 * 
 * export default function MyComponent() {
 *   const [loading, setLoading] = useState(false);
 * 
 *   const handleSubmit = async (data) => {
 *     try {
 *       setLoading(true);
 *       const response = await api.post('/endpoint', data);
 *       success('Datos guardados correctamente');
 *     } catch (err) {
 *       error(err.response?.data?.error || 'Error desconocido');
 *     } finally {
 *       setLoading(false);
 *     }
 *   };
 * 
 *   return (
 *     <button onClick={() => handleSubmit({...})}>
 *       Guardar
 *     </button>
 *   );
 * }
 */
