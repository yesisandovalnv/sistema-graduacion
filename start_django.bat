@echo off
cd /d c:\Users\luisfer\Documents\Visual-Code\sistema-graduacion
call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
