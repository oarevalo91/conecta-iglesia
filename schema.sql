PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS miembros (
 id INTEGER PRIMARY KEY,
 nombres TEXT NOT NULL CHECK(length(trim(nombres)) BETWEEN 1 AND 100),
 apellidos TEXT NOT NULL CHECK(length(trim(apellidos)) BETWEEN 1 AND 100),
 telefono TEXT,
 correo TEXT,
 direccion TEXT CHECK(direccion IS NULL OR length(direccion) <= 250),
 bautizado TEXT CHECK(bautizado IN ('si','no') OR bautizado IS NULL),
 fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- Las siguientes tablas preparan el modelo; sus pantallas no forman parte de este CRUD.
CREATE TABLE IF NOT EXISTS servicios (
 id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, fecha TEXT NOT NULL, hora TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS usuarios (
 id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, correo TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL, rol TEXT NOT NULL DEFAULT 'lider'
);
CREATE TABLE IF NOT EXISTS asistencias (
 id INTEGER PRIMARY KEY,
 miembro_id INTEGER NOT NULL REFERENCES miembros(id) ON DELETE RESTRICT,
 servicio_id INTEGER NOT NULL REFERENCES servicios(id) ON DELETE RESTRICT,
 UNIQUE(miembro_id, servicio_id)
);
CREATE TABLE IF NOT EXISTS seguimientos (
 id INTEGER PRIMARY KEY,
 miembro_id INTEGER NOT NULL REFERENCES miembros(id) ON DELETE RESTRICT,
 usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
 fecha TEXT NOT NULL,
 estado TEXT NOT NULL CHECK(estado IN ('pendiente','realizado')) DEFAULT 'pendiente'
);
