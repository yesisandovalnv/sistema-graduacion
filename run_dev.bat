@echo off
REM Cargar variables de entorno de desarrollo
for /f "tokens=*" %%i in (.env.development) do set %%i

REM Ejecutar Django en modo desarrollo
python manage.py runserver 0.0.0.0:8000
