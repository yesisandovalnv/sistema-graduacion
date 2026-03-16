from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django_celery_results.models import TaskResult

from postulantes.models import Notificacion


@shared_task
def limpiar_notificaciones_antiguas():
    """
    Elimina las notificaciones que han sido leÃ­das y tienen mÃ¡s de 30 dÃ­as de antigÃ¼edad.
    TambiÃ©n elimina los resultados de tareas exitosas con mÃ¡s de 30 dÃ­as de antigÃ¼edad.
    """
    limite_fecha = timezone.now() - timedelta(days=30)

    # 1. Limpiar notificaciones leÃ­das y antiguas
    notificaciones_a_borrar = Notificacion.objects.filter(
        leida=True,
        fecha_creacion__lt=limite_fecha
    )
    count_notif, _ = notificaciones_a_borrar.delete()

    # 2. Limpiar resultados de tareas exitosas y antiguas
    task_results_a_borrar = TaskResult.objects.filter(
        status='SUCCESS',
        date_done__lt=limite_fecha
    )
    count_tasks, _ = task_results_a_borrar.delete()

    return f"Se eliminaron {count_notif} notificaciones y {count_tasks} resultados de tareas antiguas."
