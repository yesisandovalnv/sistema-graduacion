#!/usr/bin/env python
"""
🧪 HERRAMIENTA INTERACTIVA: Test de datos en tiempo real
Ver, agregar y probar datos uno a uno en el endpoint de gráficos
"""
import os
import sys
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db.models import Count, Q
from django.utils import timezone
from postulantes.models import Postulacion, Postulante
from modalidades.models import Modalidad
from usuarios.models import CustomUser

def separador(titulo=""):
    if titulo:
        print(f"\n{'═' * 80}")
        print(f"  {titulo}")
        print(f"{'═' * 80}\n")
    else:
        print(f"\n{'-' * 80}\n")

def mostrar_datos_actuales():
    """Mostrar estado actual de la BD"""
    separador("📊 DATOS ACTUALES EN BASE DE DATOS")
    
    total_postulantes = Postulante.objects.count()
    total_postulaciones = Postulacion.objects.count()
    
    print(f"✅ Total Postulantes: {total_postulantes}")
    print(f"✅ Total Postulaciones: {total_postulaciones}")
    
    if total_postulaciones > 0:
        # Distribución por estado
        print(f"\n📈 Distribución por Estado:")
        estados = Postulacion.objects.values('estado_general').annotate(
            total=Count('id')
        ).order_by('-total')
        
        for est in estados:
            estado = est['estado_general']
            total = est['total']
            print(f"   • {estado}: {total}")
        
        # Últimas 5 postulaciones
        print(f"\n📝 Últimas 5 Postulaciones:")
        ultimas = Postulacion.objects.order_by('-fecha_postulacion')[:5]
        for i, post in enumerate(ultimas, 1):
            postulante_nombre = f"{post.postulante.primer_nombre} {post.postulante.primer_apellido}" if post.postulante else "N/A"
            print(f"   {i}. {postulante_nombre} - {post.estado_general} ({post.fecha_postulacion.date()})")
    else:
        print("   ⚠️  SIN DATOS - La base de datos está vacía")

def obtener_datos_graficos():
    """Obtener datos del endpoint"""
    separador("📡 DATOS DEL ENDPOINT")
    
    try:
        from reportes.services import get_dashboard_chart_data
        
        data = get_dashboard_chart_data(meses=6)
        
        print("✅ pieChartData (Distribución de Estados):")
        if data.get('pieChartData'):
            total_pie = sum(item['value'] for item in data['pieChartData'])
            for item in data['pieChartData']:
                pct = (item['value'] / total_pie * 100) if total_pie > 0 else 0
                print(f"   • {item['name']:20} {item['value']:3} ({pct:5.1f}%)")
        else:
            print("   ❌ VACÍO")
        
        print(f"\n✅ barChartData (Postulantes & Documentos):")
        if data.get('barChartData'):
            for item in data['barChartData'][:6]:
                print(f"   • {item['semana']:10} postulantes={item['postulantes']:3}  documentos={item['documentos']:3}")
        else:
            print("   ❌ VACÍO")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def agregar_postulacion_manual():
    """Agregar una nueva postulación interactivamente"""
    separador("➕ AGREGAR NUEVA POSTULACIÓN")
    
    try:
        # Obtener modalidad
        modalidad = Modalidad.objects.first()
        if not modalidad:
            print("❌ Error: No hay modalidades disponibles")
            return False
        
        # Obtener o crear postulante de prueba
        postulante, _ = Postulante.objects.get_or_create(
            ci='9999999',
            defaults={
                'primer_nombre': 'Test',
                'primer_apellido': 'Usuario',
                'email': f'test@test{Postulante.objects.count()}.local',
            }
        )
        
        # Estados disponibles
        estados_disponibles = ['TITULADO', 'APROBADO', 'EN_PROCESO', 'RECHAZADO']
        print(f"\n📋 Estados disponibles:")
        for i, est in enumerate(estados_disponibles, 1):
            print(f"   {i}. {est}")
        
        opcion = input("\n🔤 Selecciona estado (número): ").strip()
        try:
            idx = int(opcion) - 1
            if idx < 0 or idx >= len(estados_disponibles):
                print("❌ Opción inválida")
                return False
            estado = estados_disponibles[idx]
        except:
            print("❌ Entrada inválida")
            return False
        
        # Crear postulación
        post = Postulacion.objects.create(
            postulante=postulante,
            modalidad=modalidad,
            carrera=postulante.carrera or 'No especificada',
            codigo_estudiante=postulante.codigo_estudiante or f'EST{Postulacion.objects.count()}',
            estado_general=estado,
            fecha_postulacion=timezone.now()
        )
        
        print(f"\n✅ Postulación creada exitosamente")
        print(f"   • ID: {post.id}")
        print(f"   • Postulante: {postulante.primer_nombre} {postulante.primer_apellido}")
        print(f"   • Estado: {estado}")
        print(f"   • Fecha: {post.fecha_postulacion}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def limpiar_datos():
    """Limpiar todas las postulaciones (para testing limpio)"""
    separador("🗑️  LIMPIAR BASE DE DATOS")
    
    total = Postulacion.objects.count()
    print(f"⚠️  Esto eliminará {total} postulaciones")
    confirmar = input("\n¿Estás seguro? (s/n): ").strip().lower()
    
    if confirmar == 's':
        Postulacion.objects.all().delete()
        print("✅ Datos eliminados")
        return True
    else:
        print("❌ Cancelado")
        return False

def generar_datos_test():
    """Generar datos de prueba rápidamente"""
    separador("🔄 GENERAR DATOS DE PRUEBA")
    
    try:
        modalidad = Modalidad.objects.first()
        if not modalidad:
            print("❌ No hay modalidades disponibles")
            return False
        
        estados = ['TITULADO', 'APROBADO', 'EN_PROCESO', 'RECHAZADO']
        cantidad = 20
        
        print(f"Generando {cantidad} postulaciones...")
        
        for i in range(cantidad):
            postulante, _ = Postulante.objects.get_or_create(
                ci=f'CI-TEST-{i:04d}',
                defaults={
                    'primer_nombre': f'Test{i}',
                    'primer_apellido': f'Usuario{i}',
                    'email': f'test{i}@test.local',
                }
            )
            
            estado = estados[i % len(estados)]
            
            Postulacion.objects.create(
                postulante=postulante,
                modalidad=modalidad,
                carrera='Ingeniería',
                codigo_estudiante=f'EST-{i:04d}',
                estado_general=estado,
                fecha_postulacion=timezone.now() - timedelta(days=i % 30)
            )
            
            if (i + 1) % 5 == 0:
                print(f"  ... {i + 1}/{cantidad}")
        
        print(f"✅ {cantidad} postulaciones creadas")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def menu_principal():
    """Menú interactivo"""
    while True:
        separador("🎯 HERRAMIENTA DE TEST - DATOS DE GRÁFICOS")
        
        print("""
opciones:
  1. Ver datos actuales
  2. Ver datos en endpoint
  3. Agregar 1 postulación (manual)
  4. Generar 20 postulaciones de prueba
  5. Limpiar todos los datos
  6. Actualizar y ver cambios (ciclo)
  7. Salir
        """)
        
        opcion = input("🔤 Opción (1-7): ").strip()
        
        if opcion == '1':
            mostrar_datos_actuales()
            input("\n▶️  Presiona ENTER para continuar...")
        
        elif opcion == '2':
            obtener_datos_graficos()
            input("\n▶️  Presiona ENTER para continuar...")
        
        elif opcion == '3':
            if agregar_postulacion_manual():
                print("\n" + "─" * 80)
                print("📊 DATOS DESPUÉS DE AGREGAR:")
                mostrar_datos_actuales()
                print("\n" + "─" * 80)
                print("📡 ENDPOINT DESPUÉS DE AGREGAR:")
                obtener_datos_graficos()
            input("\n▶️  Presiona ENTER para continuar...")
        
        elif opcion == '4':
            if generar_datos_test():
                print("\n" + "─" * 80)
                print("📊 DATOS DESPUÉS:")
                mostrar_datos_actuales()
                print("\n" + "─" * 80)
                print("📡 ENDPOINT DESPUÉS:")
                obtener_datos_graficos()
            input("\n▶️  Presiona ENTER para continuar...")
        
        elif opcion == '5':
            if limpiar_datos():
                print("\n" + "─" * 80)
                print("📊 DATOS DESPUÉS DE LIMPIAR:")
                mostrar_datos_actuales()
            input("\n▶️  Presiona ENTER para continuar...")
        
        elif opcion == '6':
            print("📊 Mostrando datos en tiempo real...")
            print("(Agrega datos en otra ventana y presiona ENTER para actualizar)\n")
            
            while True:
                print("\n" + "═" * 80)
                print(f"  🕐 {datetime.now().strftime('%H:%M:%S')}")
                print("═" * 80 + "\n")
                
                mostrar_datos_actuales()
                print("\n" + "-" * 80)
                obtener_datos_graficos()
                
                continuar = input("\n▶️  Presiona ENTER para actualizar (o 'q' para salir): ").strip().lower()
                if continuar == 'q':
                    break
        
        elif opcion == '7':
            print("✅ Adiós!")
            break
        
        else:
            print("❌ Opción inválida")
            input("\n▶️  Presiona ENTER para continuar...")

if __name__ == '__main__':
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n✅ Herramienta cerrada")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
