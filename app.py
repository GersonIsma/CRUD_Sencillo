from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Obtén la URL y valídala
database_url = os.environ.get('DATABASE_URL')
print("DATABASE_URL from env:", database_url)  # Depuración (ver logs en Render)

if not database_url:
    raise ValueError("No se encontró DATABASE_URL en las variables de entorno.")

# Corrige el formato si es necesario
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    nombre = request.args.get('nombre')
    users = []
    if nombre:
        users = User.query.filter(User.name.ilike(f"%{nombre}%")).all()
    return render_template('home.html', users=users)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        db.session.add(User(name=name, email=email))
        db.session.commit()
        return redirect('/')
    return render_template('agregar.html')

@app.route('/consultar')
def consultar():
    nombre = request.args.get('nombre')
    ver_todos = request.args.get('todos')
    users = []

    if nombre:
        users = User.query.filter(User.name.ilike(f"%{nombre}%")).all()
    elif ver_todos:
        users = User.query.all()

    return render_template('consultar.html', users=users)

@app.route('/consultar/<int:id>')
def consultar_uno(id):
    user = User.query.get_or_404(id)
    return render_template('ver_usuario.html', user=user)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        db.session.commit()
        return redirect('/consultar')
    return render_template('editar.html', user=user)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/consultar')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Usa el puerto de Render o 5000 por defecto
    app.run(host='0.0.0.0', port=port)  # ¡Asegúrate de usar 0.0.0.0!
