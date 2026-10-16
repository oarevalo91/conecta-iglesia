# Conecta Iglesia — Corte I

Aplicación académica local para organizar miembros de la iglesia y preparar el futuro registro de asistencia y seguimiento pastoral.

## Alcance implementado
Crear, listar, buscar por nombres o apellidos, editar y eliminar miembros con confirmación. Teléfono, correo y dirección opcionales. Bautismo con selección Sí/No obligatoria; registros anteriores pendientes hasta completar. Validación en servidor, CSRF, SQL parametrizado e integridad referencial. Las tablas de servicios, usuarios, asistencias y seguimientos están creadas; sus pantallas y autenticación quedan para etapas posteriores. No existe envío de mensajes ni integración de IA en esta versión.

## Integrantes
Obed Arévalo. Completar los demás integrantes y el nombre del grupo antes de entregar.

## Tecnologías
Python 3.10 o superior, Flask, Flask-WTF y SQLite (incluido en Python).
Se utilizan consultas SQL directas con sqlite3 en lugar de SQLAlchemy para facilitar el estudio del SQL. Esta es una decisión de implementación propuesta por el asistente.

## Instalar y ejecutar en Windows
1. Instala Python desde python.org y habilita la opción de agregarlo al PATH.
2. Descomprime el ZIP y abre una terminal dentro de la carpeta `conecta_iglesia`.
3. Ejecuta, una línea a la vez:

```bat
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
```

4. Abre http://127.0.0.1:5000 en el navegador. Mantén la terminal abierta; para detener pulsa Ctrl+C.
5. Para volver a abrirlo otro día, ejecuta `.venv\Scripts\python app.py` desde esa carpeta.

## Linux o macOS
```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

## Datos de demostración opcionales
Detén el servidor y ejecuta:
```bat
.venv\Scripts\python -m flask --app app:create_app datos-demo
```
En Linux/macOS sustituye el ejecutable por `.venv/bin/python`. Después vuelve a iniciar la aplicación. Solo agrega tres miembros ficticios si la tabla está vacía.

## Base de datos
La primera ejecución crea `instance/conecta_iglesia.db` y aplica `schema.sql` sin borrar tablas existentes. No debes crear el archivo manualmente. SQLite guarda fechas de registro en UTC. Los nombres pueden repetirse: no son identificadores únicos. No se exige correo único a miembros porque familias pueden compartirlo.

Relaciones: Miembro 1 a 0..N Asistencia; Servicio 1 a 0..N Asistencia; Miembro 1 a 0..N Seguimiento; Usuario 1 a 0..N Seguimiento. Cada asistencia tiene un miembro y un servicio; no se permite repetir la pareja. Cada seguimiento tiene un miembro y un responsable. Las claves foráneas impiden eliminar miembros con historial.

## Verificar
```bat
.venv\Scripts\python -m unittest -v
```
Las ocho pruebas automatizadas utilizan una base temporal y verifican CRUD, persistencia, búsqueda Unicode, datos inválidos, CSRF, registro inexistente, integridad y escape HTML. Pasaron en el entorno del asistente durante la preparación. No sustituyen la prueba local del equipo.

Prueba manual: crear un miembro sin teléfono ni correo; buscarlo; editarlo; cancelar una eliminación; confirmar otra; probar nombres vacíos y correo inválido; cerrar y reiniciar; revisar a ancho de celular.

## Cómo explicar el código
- `app.py`: formularios y validaciones, conexión por solicitud, rutas y comando de datos ficticios.
- `schema.sql`: cinco tablas, claves y restricciones.
- `templates/`: listado, formulario y confirmación con Jinja2.
- `static/estilos.css`: diseño adaptable.
- `test_app.py`: pruebas con unittest y cliente de Flask.

GET consulta; POST modifica. El enlace Eliminar abre una confirmación, y solo el formulario POST borra. Los signos `?` son parámetros para separar datos y SQL. `commit()` confirma un cambio; `rollback()` lo revierte cuando SQLite bloquea una eliminación.

## Uso local y próximos pasos
Esta versión no tiene login y debe usarse localmente con datos ficticios. El servidor escucha solo en 127.0.0.1 y debug está desactivado. Se genera una clave local persistente excluida de Git; también puede configurarse SECRET_KEY en el entorno. Antes de usar datos reales o publicar hacen falta autenticación, permisos, revisión de privacidad, HTTPS y un despliegue apropiado.

## GitHub
Repositorio aún no creado. Crear uno e invitar al equipo. No subir `.venv`, `instance`, `.env`, bases con datos ni claves. Cada integrante debe realizar y comprender aportes reales; no se han fabricado commits ni firmas.

## Entrega académica pendiente
Este paquete es el primer módulo, no la entrega académica completa. Faltan completar integrantes, enlace GitHub y aportes de todos, PDF formal del problema y requisitos, prototipo del sistema completo y bitácora firmada con al menos cuatro usos reales. Conservar el registro de esta interacción; no inventar errores ni decisiones del equipo.

## Actualización de una instalación anterior
Consulta ACTUALIZAR.md. Se agregan dirección y bautismo sin borrar registros, con respaldo automático previo.
