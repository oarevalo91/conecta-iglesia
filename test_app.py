import re
import sqlite3
import tempfile
import unittest
from pathlib import Path
from app import create_app

class CRUDTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name)/'test.db')
        self.app = create_app({'TESTING':True,'DATABASE':self.path,'SECRET_KEY':'solo-pruebas'})
        self.client = self.app.test_client()
    def tearDown(self): self.tmp.cleanup()
    def token(self,url):
        html = self.client.get(url).get_data(as_text=True)
        return re.search(r'name="csrf_token"[^>]*value="([^"]+)"',html).group(1)
    def post(self,url,**data):
        data.setdefault('bautizado','no')
        data['csrf_token']=self.token(url)
        return self.client.post(url,data=data,follow_redirects=True)
    def count(self):
        with sqlite3.connect(self.path) as db:return db.execute('SELECT count(*) FROM miembros').fetchone()[0]
    def test_crud_search_and_persistence(self):
        r=self.post('/miembros/nuevo',nombres='José',apellidos='Ejemplo')
        self.assertIn('registrado correctamente',r.get_data(as_text=True)); self.assertEqual(self.count(),1)
        self.assertIn('José',self.client.get('/?q=JOSÉ').get_data(as_text=True))
        self.post('/miembros/1/editar',nombres='Ana',apellidos='Prueba',correo='ana@example.com')
        self.assertIn('Ana',self.client.get('/').get_data(as_text=True))
        reopened=create_app({'TESTING':True,'DATABASE':self.path,'SECRET_KEY':'solo-pruebas'})
        self.assertIn('Ana',reopened.test_client().get('/').get_data(as_text=True))
        self.client.get('/miembros/1/eliminar'); self.assertEqual(self.count(),1)
        self.post('/miembros/1/eliminar'); self.assertEqual(self.count(),0)
    def test_invalid_fields(self):
        for fields in [dict(nombres=' ',apellidos='X'),dict(nombres='Ana',apellidos='X',correo='mal'),dict(nombres='Ana',apellidos='X',telefono='abc'),dict(nombres='A'*101,apellidos='X')]:
            self.post('/miembros/nuevo',**fields)
        self.assertEqual(self.count(),0)
    def test_new_fields_and_validation(self):
        self.post('/miembros/nuevo',nombres='Ana',apellidos='Prueba',direccion='Calle ficticia 123',bautizado='si')
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute('SELECT direccion,bautizado FROM miembros').fetchone(),('Calle ficticia 123','si'))
        self.post('/miembros/1/editar',nombres='Ana',apellidos='Prueba',direccion='',bautizado='no')
        with sqlite3.connect(self.path) as db:self.assertEqual(db.execute('SELECT direccion,bautizado FROM miembros').fetchone(),(None,'no'))
        for value in ['', 'inventado']:
            self.post('/miembros/nuevo',nombres='Otra',apellidos='Prueba',bautizado=value)
        self.post('/miembros/nuevo',nombres='Otra',apellidos='Prueba',direccion='x'*251,bautizado='si')
        self.assertEqual(self.count(),1)
    def test_old_database_migration(self):
        old = str(Path(self.tmp.name)/'anterior.db')
        with sqlite3.connect(old) as db:
            db.execute('CREATE TABLE miembros(id INTEGER PRIMARY KEY,nombres TEXT,apellidos TEXT,telefono TEXT,correo TEXT,fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP)')
            db.execute("INSERT INTO miembros(nombres,apellidos) VALUES('José','Anterior')")
        app=create_app({'TESTING':True,'DATABASE':old,'SECRET_KEY':'solo-pruebas'})
        with sqlite3.connect(old) as db:self.assertEqual(db.execute('SELECT nombres,direccion,bautizado FROM miembros').fetchone(),('José',None,None))
        self.assertIn('Pendiente',app.test_client().get('/').get_data(as_text=True))
        self.assertEqual(len(list(Path(self.tmp.name).glob('anterior.db.respaldo*'))),1)
        create_app({'TESTING':True,'DATABASE':old,'SECRET_KEY':'solo-pruebas'})
        self.assertEqual(len(list(Path(self.tmp.name).glob('anterior.db.respaldo*'))),1)
    def test_csrf_missing(self):
        self.assertEqual(self.client.post('/miembros/nuevo',data={'nombres':'Ana','apellidos':'X'}).status_code,400)
    def test_missing_member(self):
        self.assertEqual(self.client.get('/miembros/999/editar').status_code,404)
    def test_history_blocks_delete(self):
        self.post('/miembros/nuevo',nombres='Ana',apellidos='X')
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO servicios(nombre,fecha,hora) VALUES('Ejemplo','2026-10-15','18:30')")
            db.execute('INSERT INTO asistencias(miembro_id,servicio_id) VALUES(1,1)')
        result=self.post('/miembros/1/eliminar')
        self.assertEqual(self.count(),1)
        self.assertIn('No se puede eliminar',result.get_data(as_text=True))
    def test_parameterized_search_and_escaping(self):
        self.post('/miembros/nuevo',nombres='<script>alert(1)</script>',apellidos='Ejemplo')
        self.assertNotIn('<script>alert(1)</script>',self.client.get('/').get_data(as_text=True))
        self.client.get('/?q=%27%20OR%201%3D1--');self.assertEqual(self.count(),1)

if __name__=='__main__':unittest.main(verbosity=2)
