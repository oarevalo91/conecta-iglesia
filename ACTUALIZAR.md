# Actualización: dirección y bautismo

1. Detén el servidor con Ctrl+C en la terminal donde está ejecutándose.
2. Haz una copia de la carpeta actual del proyecto como respaldo.
3. Descomprime el ZIP actualizado en otra ubicación.
4. Copia su contenido sobre tu carpeta original `conecta_iglesia`, reemplazando los archivos del programa. Conserva las carpetas `instance` y `.venv` originales; no las borres ni las reemplaces.
5. Desde tu carpeta original ejecuta:

```powershell
.\.venv\Scripts\python.exe app.py
```

6. Abre http://127.0.0.1:5000 y actualiza la página con Ctrl+F5.

La actualización añade columnas a la base existente sin borrar miembros. Antes de hacerlo crea un archivo de respaldo junto a la base dentro de `instance`. No cambies la base por otra vacía.

Dirección: opcional, máximo 250 caracteres. Bautizado/a: selecciona Sí o No al registrar o editar. Los miembros anteriores conservan el dato vacío y muestran Pendiente, porque no conocemos su respuesta. No se asigna No automáticamente.

Prueba ambos valores, dirección vacía y completa, edición y persistencia tras reiniciar. No publiques la base ni sus respaldos en GitHub. Utiliza datos ficticios para las evidencias académicas.
