# Informe básico de seguridad web

## Alcance

Aplicación Flask ejecutada únicamente en `http://127.0.0.1:5000`. Se revisaron las páginas HTML, recursos estáticos y endpoints `/api/bomberos`. No se realizó escaneo contra Neon ni otros sistemas ajenos.

## Herramienta

- OWASP ZAP o Burp Suite Community.
- Fecha:
- Versión utilizada:
- Tipo de análisis: pasivo / activo autorizado localmente.

## Evidencias

Agregar las capturas de pantalla dentro de esta carpeta:

- `zap_inicio.png`: objetivo y configuración del escaneo.
- `zap_alertas.png`: resumen de hallazgos.
- `zap_detalle.png`: detalle de una alerta y URL afectada.
- `zap_informe.pdf` o `zap_informe.html`: informe exportado.

## Hallazgos

Completa una fila por cada alerta confirmada o descartada:

| Hallazgo | Riesgo | Evidencia | Interpretación | Medida preventiva |
|---|---|---|---|---|
| Ejemplo: falta de cabecera CSP | Informativo/Bajo | Captura ZAP | El navegador recibe una política sin restricciones específicas | Configurar CSP restrictiva; probar recursos propios |
| Ejemplo: falta de autenticación | Alto | Ruta `/api/bomberos` accesible | Cualquier usuario puede listar, crear o modificar registros | Implementar inicio de sesión, roles y autorización |
| Ejemplo: servidor de desarrollo | Medio | Respuesta de Flask en local | Flask integrado no está diseñado como servidor productivo | Usar Waitress/Gunicorn detrás de HTTPS |

No presentes como vulnerabilidad real una alerta hasta verificarla manualmente. Explica las falsas positivas si aparecen.

## Controles implementados

- Validación de DNI de ocho dígitos.
- Validación de nombres, apellidos y especialidades.
- DNI único en la base de datos.
- Protección básica contra marcos externos mediante `X-Frame-Options: DENY`.
- `X-Content-Type-Options: nosniff`.
- Política de recursos `Content-Security-Policy`.
- Restricción de APIs del navegador mediante `Permissions-Policy`.
- `Referrer-Policy`.
- Credenciales de Neon fuera del repositorio mediante `.env`.
- Modo debug desactivado.

## Acciones pendientes antes de publicar

1. Implementar autenticación y autorización.
2. Limitar intentos y registrar auditoría.
3. Configurar HTTPS y despliegue con servidor WSGI.
4. Revisar el manejo de errores y evitar respuestas técnicas innecesarias.
5. Rotar periódicamente credenciales y usar variables de entorno.

## Conclusiones

Redactar exactamente cuatro conclusiones, también para el video:

1. Las pruebas funcionales automatizadas permiten validar CRUD y evitar regresiones.
2. La seguridad debe verificarse desde el inicio y no solo al finalizar.
3. Las herramientas detectan posibles riesgos, pero la interpretación humana confirma o descarta resultados.
4. La protección de datos y la autenticación son esenciales antes de publicar una aplicación.
