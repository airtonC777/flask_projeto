from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Remover o banco de dados existente, se houver
if os.path.exists("pagamentos.db"):
    os.remove("pagamentos.db")

# Inicializar o app e o banco
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pagamentos.db'
db = SQLAlchemy(app)

# Definir os modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clube = db.Column(db.String(100))
    igreja = db.Column(db.String(100))
    regiao = db.Column(db.String(100))
    categoria = db.Column(db.String(100))
    total = db.Column(db.String)
    janeiro = db.Column(db.String)
    fevereiro = db.Column(db.String)
    marco = db.Column(db.String)
    abril = db.Column(db.String)
    maio = db.Column(db.String)
    junho = db.Column(db.String)
    julho = db.Column(db.String)
    agosto = db.Column(db.String)
    setembro = db.Column(db.String)
    outubro = db.Column(db.String)
    novembro = db.Column(db.String)
    dezembro = db.Column(db.String)

# Criar as tabelas no banco
with app.app_context():
    db.create_all()

print("Banco de dados pagamentos.db criado com sucesso com todas as colunas do modelo Pagamento.")
