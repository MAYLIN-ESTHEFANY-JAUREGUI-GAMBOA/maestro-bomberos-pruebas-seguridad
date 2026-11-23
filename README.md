# Maestro de Bomberos

Aplicación web de gestión de personal con Flask, SQLAlchemy, PostgreSQL (Neon), HTML, CSS y JavaScript. Incluye alta, consulta, edición, cambio de estado y eliminación; validación del lado del servidor; filtro por estado y búsqueda en el directorio.

## Requisitos

- Python 3.10 o superior
- Una base PostgreSQL. Neon es opcional para desarrollo local; sin `DATABASE_URL` se usa SQLite en `instance/`.

## Instalación y ejecución

En PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Configura `DATABASE_URL` en `.env` con la cadena de conexión de Neon (incluye `sslmode=require`) y cambia `SECRET_KEY` por un valor aleatorio privado. No compartas ni subas `.env`.

```powershell
python app.py
```

Abre <http://127.0.0.1:5000>. En desarrollo, si no configuras Neon, la aplicación crea/usa SQLite local. Las tablas se crean al iniciar la aplicación.

## API

| Método | Ruta | Operación |
|---|---|---|
| `GET` | `/api/bomberos` | Listar; admite `?estado=activo` o `?estado=inactivo` |
| `POST` | `/api/bomberos` | Registrar |
| `GET` | `/api/bomberos/<id>` | Consultar |
| `PUT` | `/api/bomberos/<id>` | Actualizar datos |
| `PATCH` | `/api/bomberos/<id>/estado` | Activar/desactivar (`{"estado": true}`) |
| `DELETE` | `/api/bomberos/<id>` | Eliminar |

El DNI debe tener ocho dígitos; la especialidad debe ser Rescate, Incendios o Primeros auxilios.

## Pruebas

Pruebas de API y validaciones (SQLite temporal, no necesita Neon):

```powershell
pytest -q
```

La automatización Selenium requiere Chrome/Chromium y su driver disponible para Selenium Manager:

```powershell
$env:RUN_SELENIUM = "1"
pytest -q tests/e2e
```

La prueba abre la aplicación en modo headless, registra un bombero desde la interfaz, comprueba el directorio y limpia el registro.

## Selenium, Playwright y análisis con OWASP ZAP

### Selenium frente a Playwright

| Aspecto | Selenium | Playwright |
|---|---|---|
| Rendimiento | Bueno; cada acción usa WebDriver y puede necesitar más esperas explícitas | Generalmente más rápido; usa controles directos sobre el navegador |
| Facilidad de uso | API madura y ampliamente conocida; requiere entender WebDriver y condiciones de espera | API moderna y uniforme; incluye esperas automáticas y herramientas integradas |
| Navegadores | Chrome, Firefox, Edge y otros mediante drivers | Chromium, Firefox y WebKit |
| Evidencias | Capturas mediante código | Capturas, video y trazas integradas |
| Ecosistema | Muy amplio y adecuado para proyectos institucionales y variados | Crece rápidamente y es fuerte en pruebas modernas |
| Paralelismo | Disponible, aunque depende de configuración | API y ejecución multircontexto más simples |

Este proyecto usa Selenium porque cumple explícitamente el criterio de la actividad y demuestra el flujo real. Playwright no se instala para evitar mantener dos soluciones que hacen lo mismo. Conceptualmente, Playwright suele ser más cómodo para pruebas rápidas y trazas; Selenium ofrece mayor familiaridad, compatibilidad y integración tradicional.


