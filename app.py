"""Primer corte: CRUD local de miembros con SQLite y validación en servidor."""
import os
import secrets
import sqlite3
from pathlib import Path
import click
from flask import Flask, g, render_template, request, redirect, url_for, flash, abort
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional, Email, Regexp

class MiembroForm(FlaskForm):
    nombres = StringField('Nombres', filters=[lambda v: v.strip() if v else v], validators=[DataRequired(message='Ingresa los nombres.'), Length(max=100)])
    apellidos = StringField('Apellidos', filters=[lambda v: v.strip() if v else v], validators=[DataRequired(message='Ingresa los apellidos.'), Length(max=100)])
    telefono = StringField('Teléfono (opcional)', filters=[lambda v: v.strip() if v else v], validators=[Optional(), Length(max=25), Regexp(r'^\+?[0-9 ()-]{7,25}$', message='Usa entre 7 y 25 caracteres: números, espacios, +, paréntesis o guiones.')])
    correo = StringField('Correo (opcional)', filters=[lambda v: v.strip() if v else v], validators=[Optional(), Length(max=254), Email(message='Ingresa un correo válido.', check_deliverability=False)])
    direccion = StringField('Dirección (opcional)', filters=[lambda v: v.strip() if v else v], validators=[Optional(), Length(max=250)])
    bautizado = SelectField('¿Es bautizado/a?', choices=[('', 'Selecciona una respuesta'), ('si', 'Sí'), ('no', 'No')], validators=[DataRequired(message='Selecciona Sí o No.')])
    guardar = SubmitField('Guardar miembro')

class EliminarForm(FlaskForm):
    eliminar = SubmitField('Sí, eliminar miembro')

def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    # Clave local persistente, fuera del repositorio; puede sustituirse por SECRET_KEY.
    key_file = Path(app.instance_path) / 'clave_local'
    if not key_file.exists():
        try:
            with key_file.open('x') as f: f.write(secrets.token_hex(32))
            key_file.chmod(0o600)
        except FileExistsError:
            pass
    app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or key_file.read_text(), DATABASE=str(Path(app.instance_path)/'conecta_iglesia.db'), MAX_CONTENT_LENGTH=1024*1024, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
    if config: app.config.update(config)
    CSRFProtect(app)

    def db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
            g.db.execute('PRAGMA foreign_keys = ON')
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        connection = g.pop('db', None)
        if connection is not None: connection.close()

    with app.app_context():
        # Migración aditiva: conservar datos y no asumir el bautismo de miembros anteriores.
        connection = db()
        exists = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='miembros'").fetchone()
        if exists:
            columns = {row['name'] for row in connection.execute('PRAGMA table_info(miembros)')}
            if not {'direccion', 'bautizado'}.issubset(columns):
                from datetime import datetime
                backup_path = str(app.config['DATABASE']) + '.respaldo_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.db'
                with sqlite3.connect(backup_path) as backup:
                    connection.backup(backup)
                if 'direccion' not in columns:
                    connection.execute('ALTER TABLE miembros ADD COLUMN direccion TEXT CHECK(direccion IS NULL OR length(direccion) <= 250)')
                if 'bautizado' not in columns:
                    connection.execute("ALTER TABLE miembros ADD COLUMN bautizado TEXT CHECK(bautizado IN ('si','no') OR bautizado IS NULL)")
                connection.commit()
        db().executescript((Path(__file__).parent/'schema.sql').read_text(encoding='utf-8'))

    def member_or_404(id):
        row = db().execute('SELECT * FROM miembros WHERE id = ?', (id,)).fetchone()
        if row is None: abort(404)
        return row

    @app.route('/')
    def index():
        q = request.args.get('q', '').strip()[:100]
        # casefold permite buscar nombres con mayúsculas y minúsculas Unicode.
        db().create_function('CASEFOLD', 1, lambda v: v.casefold() if v else '')
        rows = db().execute("SELECT * FROM miembros WHERE instr(CASEFOLD(nombres || ' ' || apellidos), CASEFOLD(?)) > 0 ORDER BY apellidos, nombres", (q,)).fetchall()
        total = db().execute('SELECT COUNT(*) FROM miembros').fetchone()[0]
        return render_template('lista.html', miembros=rows, q=q, total=total)

    @app.route('/miembros/nuevo', methods=['GET','POST'])
    def nuevo():
        form = MiembroForm()
        if form.validate_on_submit():
            db().execute('INSERT INTO miembros(nombres, apellidos, telefono, correo, direccion, bautizado) VALUES(?,?,?,?,?,?)', (form.nombres.data, form.apellidos.data, form.telefono.data or None, form.correo.data or None, form.direccion.data or None, form.bautizado.data))
            db().commit()
            flash('Miembro registrado correctamente.')
            return redirect(url_for('index'))
        return render_template('formulario.html', form=form, titulo='Registrar miembro')

    @app.route('/miembros/<int:id>/editar', methods=['GET','POST'])
    def editar(id):
        miembro = member_or_404(id)
        form = MiembroForm(data={**dict(miembro), 'bautizado': miembro['bautizado'] or ''}) if request.method == 'GET' else MiembroForm()
        if form.validate_on_submit():
            db().execute('UPDATE miembros SET nombres=?, apellidos=?, telefono=?, correo=?, direccion=?, bautizado=? WHERE id=?', (form.nombres.data, form.apellidos.data, form.telefono.data or None, form.correo.data or None, form.direccion.data or None, form.bautizado.data, id))
            db().commit()
            flash('Información actualizada.')
            return redirect(url_for('index'))
        return render_template('formulario.html', form=form, titulo='Editar miembro')

    @app.route('/miembros/<int:id>/eliminar', methods=['GET','POST'])
    def eliminar(id):
        miembro = member_or_404(id)
        form = EliminarForm()
        if form.validate_on_submit():
            try:
                db().execute('DELETE FROM miembros WHERE id=?',(id,))
                db().commit()
                flash('Miembro eliminado.')
            except sqlite3.IntegrityError:
                db().rollback()
                flash('No se puede eliminar: tiene asistencia o seguimiento asociado.')
            return redirect(url_for('index'))
        # GET solo muestra confirmación; nunca elimina.
        return render_template('eliminar.html', miembro=miembro, form=form)

    @app.cli.command('datos-demo')
    def demo():
        """Agrega tres personas ficticias una única vez en una base vacía."""
        if db().execute('SELECT COUNT(*) FROM miembros').fetchone()[0]:
            click.echo('La base ya contiene miembros; no se agregaron datos.')
            return
        db().executemany('INSERT INTO miembros(nombres,apellidos,telefono,correo) VALUES(?,?,?,?)', [('Ana','Ejemplo',None,'ana@example.com'),('José','Demostración',None,None),('Lucía','Prueba',None,'lucia@example.com')])
        db().commit()
        click.echo('Se agregaron 3 miembros ficticios.')
    return app

if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5000, debug=False)
