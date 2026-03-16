# Descripción

React frontend para Sistema de Graduación

## Instalación

```bash
npm install
```

## Desarrollo

```bash
npm run dev
```

Abre [http://localhost:5173](http://localhost:5173) en tu navegador.

## Compilación

```bash
npm run build
```

## Estructura

```
src/
├── api/              # API service layer
├── components/       # Reusable components
├── context/          # Global state (Auth)
├── hooks/            # Custom React hooks
├── pages/            # Page components
├── layouts/          # Layout components
├── router/           # React Router config
├── styles/           # Tailwind CSS
├── constants/        # Constants and configs
├── utils/            # Utility functions
├── App.jsx           # Root component
└── main.jsx          # Entry point
```

## Características

- ✅ JWT Authentication
- ✅ Protected Routes
- ✅ Context API para estado global
- ✅ Tailwind CSS
- ✅ Responsive Design
- ✅ Error Handling
- ✅ Loading States
- ✅ Auto token refresh

## Endpoints de la API

Compatible con:
- Backend Django REST Framework
- Autenticación JWT
- Endpoints en `/api/`

## Licencia

MIT
