from flask import Flask, render_template, request, redirect, url_for, send_file, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
import pandas as pd
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
import re
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pagamentos.db'
app.secret_key = 'supersecretkey'

# Inicialização
db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Modelos
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)


class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ID automático
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


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# Função para validar senha forte
def senha_forte(senha):
    if len(senha) < 8:
        return False
    if not re.search(r"[A-Z]", senha):
        return False
    if not re.search(r"[a-z]", senha):
        return False
    if not re.search(r"[0-9]", senha):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        return False
    return True


# Registro de usuário
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if not senha_forte(senha):
            flash(
                'A senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e símbolos.',
                'danger')
            return redirect(url_for('registro'))

        senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')
        if Usuario.query.filter_by(email=email).first():
            flash('Email já registrado.', 'danger')
            return redirect(url_for('registro'))
        novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário registrado com sucesso!', 'success')
        return redirect(url_for('login'))
    return render_template('registro.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas.', 'danger')
    return render_template('login.html')


# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))


# Página inicial
@app.route('/')
@login_required
def index():
    return render_template('principal.html')


# Formulário de pagamento
@app.route('/formulario', methods=['GET', 'POST'])
@login_required
def formulario():
    if request.method == 'POST':
        erros = []
        campos_obrigatorios = ['clube', 'igreja', 'regiao', 'categoria', 'total']
        for campo in campos_obrigatorios:
            if not request.form.get(campo):
                erros.append(f'O campo {campo.replace("_", " ").title()} é obrigatório.')
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('formulario.html')

        novo_pagamento = Pagamento(
            clube=request.form['clube'],
            igreja=request.form['igreja'],
            regiao=request.form['regiao'],
            categoria=request.form['categoria'],
            total=request.form['total'],
            janeiro=request.form.get('janeiro', ''),
            fevereiro=request.form.get('fevereiro', ''),
            marco=request.form.get('marco', ''),
            abril=request.form.get('abril', ''),
            maio=request.form.get('maio', ''),
            junho=request.form.get('junho', ''),
            julho=request.form.get('julho', ''),
            agosto=request.form.get('agosto', ''),
            setembro=request.form.get('setembro', ''),
            outubro=request.form.get('outubro', ''),
            novembro=request.form.get('novembro', ''),
            dezembro=request.form.get('dezembro', '')
        )
        db.session.add(novo_pagamento)
        db.session.commit()
        flash('Pagamento cadastrado com sucesso!', 'success')
        return redirect(url_for('resultado', pagamento_id=novo_pagamento.id))

    categoria_header = request.args.get('categoria', '')
    return render_template('formulario.html', categoria_header=categoria_header)


# Resultado
@app.route('/resultado/<int:pagamento_id>')
@login_required
def resultado(pagamento_id):
    pagamento = Pagamento.query.get_or_404(pagamento_id)
    return render_template('resultado.html', dados=pagamento)


# Listar
@app.route('/listar')
@login_required
def listar():
    termo = request.args.get('busca')
    if termo:
        pagamentos = Pagamento.query.filter(
            or_(
                Pagamento.clube.ilike(f"%{termo}%"),
                Pagamento.igreja.ilike(f"%{termo}%"),
                Pagamento.regiao.ilike(f"%{termo}%"),
                Pagamento.categoria.ilike(f"%{termo}%"),
                Pagamento.janeiro.ilike(f"%{termo}%"),
                Pagamento.fevereiro.ilike(f"%{termo}%"),
                Pagamento.marco.ilike(f"%{termo}%"),
                Pagamento.abril.ilike(f"%{termo}%"),
                Pagamento.maio.ilike(f"%{termo}%"),
                Pagamento.junho.ilike(f"%{termo}%"),
                Pagamento.julho.ilike(f"%{termo}%"),
                Pagamento.agosto.ilike(f"%{termo}%"),
                Pagamento.setembro.ilike(f"%{termo}%"),
                Pagamento.outubro.ilike(f"%{termo}%"),
                Pagamento.novembro.ilike(f"%{termo}%"),
                Pagamento.dezembro.ilike(f"%{termo}%"),
                Pagamento.total.ilike(f"%{termo}%")
            )
        ).all()
    else:
        pagamentos = Pagamento.query.all()
    return render_template('listar.html', pagamentos=pagamentos, termo=termo)


# Excluir
@app.route('/excluir/<int:pagamento_id>')
@login_required
def excluir(pagamento_id):
    pagamento = Pagamento.query.get_or_404(pagamento_id)
    db.session.delete(pagamento)
    db.session.commit()
    flash('Pagamento excluído com sucesso!', 'success')
    return redirect(url_for('listar'))


# Editar
@app.route('/editar/<int:pagamento_id>', methods=['GET', 'POST'])
@login_required
def editar(pagamento_id):
    pagamento = Pagamento.query.get_or_404(pagamento_id)
    if request.method == 'POST':
        erros = []
        campos_obrigatorios = ['clube', 'igreja', 'regiao', 'categoria', 'total']
        for campo in campos_obrigatorios:
            if not request.form.get(campo):
                erros.append(f'O campo {campo.replace("_", " ").title()} é obrigatório.')
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('editar.html', pagamento=pagamento)

        pagamento.clube = request.form['clube']
        pagamento.igreja = request.form['igreja']
        pagamento.regiao = request.form['regiao']
        pagamento.categoria = request.form['categoria']
        pagamento.total = request.form['total']
        pagamento.janeiro = request.form.get('janeiro', '')
        pagamento.fevereiro = request.form.get('fevereiro', '')
        pagamento.marco = request.form.get('marco', '')
        pagamento.abril = request.form.get('abril', '')
        pagamento.maio = request.form.get('maio', '')
        pagamento.junho = request.form.get('junho', '')
        pagamento.julho = request.form.get('julho', '')
        pagamento.agosto = request.form.get('agosto', '')
        pagamento.setembro = request.form.get('setembro', '')
        pagamento.outubro = request.form.get('outubro', '')
        pagamento.novembro = request.form.get('novembro', '')
        pagamento.dezembro = request.form.get('dezembro', '')
        db.session.commit()
        flash('Pagamento atualizado com sucesso!', 'success')
        return redirect(url_for('listar'))
    return render_template('editar.html', pagamento=pagamento)


# Exportar Excel
@app.route('/exportar_excel')
@login_required
def exportar_excel():
    pagamentos = Pagamento.query.all()
    dados = [{
        'ID': p.id,
        'Clube': p.clube,
        'Igreja': p.igreja,
        'Região': p.regiao,
        'Categoria': p.categoria,
        'Total': p.total,
        'Janeiro': p.janeiro,
        'Fevereiro': p.fevereiro,
        'Março': p.marco,
        'Abril': p.abril,
        'Maio': p.maio,
        'Junho': p.junho,
        'Julho': p.julho,
        'Agosto': p.agosto,
        'Setembro': p.setembro,
        'Outubro': p.outubro,
        'Novembro': p.novembro,
        'Dezembro': p.dezembro
    } for p in pagamentos]
    df = pd.DataFrame(dados)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Pagamentos')
    output.seek(0)
    return send_file(output, download_name="pagamentos.xlsx", as_attachment=True)


# Comprovante PDF
@app.route('/comprovante/<int:pagamento_id>')
@login_required
def comprovante(pagamento_id):
    pagamento = Pagamento.query.get(pagamento_id)
    if not pagamento:
        abort(404)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    # Logo centralizado
    logo_path = os.path.join(app.root_path, "static", "logo.png")
    try:
        logo = ImageReader(logo_path)
        logo_width, logo_height = 100, 100
        c.drawImage(
            logo,
            (largura - logo_width) / 2,
            altura - logo_height - 30,
            width=logo_width,
            height=logo_height,
            mask='auto'
        )
    except Exception as e:
        print("Erro ao carregar logo:", e)

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(largura / 2, altura - 150, "Comprovante de Pagamento")

    # Campos do comprovante
    c.setFont("Helvetica", 12)
    y = altura - 190

    if pagamento.id:
        c.drawString(80, y, f"ID: {pagamento.id}");
        y -= 25
    if pagamento.clube and pagamento.clube.strip():
        c.drawString(80, y, f"Clube: {pagamento.clube}");
        y -= 25
    if pagamento.igreja and pagamento.igreja.strip():
        c.drawString(80, y, f"Igreja: {pagamento.igreja}");
        y -= 25
    if pagamento.regiao and pagamento.regiao.strip():
        c.drawString(80, y, f"Região: {pagamento.regiao}");
        y -= 25
    if pagamento.categoria and pagamento.categoria.strip():
        c.drawString(80, y, f"Categoria: {pagamento.categoria}");
        y -= 25

    for mes_nome in ["janeiro", "fevereiro", "marco", "abril", "maio", "junho",
                     "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]:
        valor = getattr(pagamento, mes_nome)
        if valor and valor.strip():
            c.drawString(80, y, f"{mes_nome.capitalize()}: {valor}")
            y -= 25

    if pagamento.total and pagamento.total.strip():
        c.setFont("Helvetica-Bold", 12)
        c.drawString(80, y - 10, f"Total: {pagamento.total}")
        y -= 35

    # Data de emissão
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(80, y - 20, f"Data de emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Assinatura centralizada
    assinatura_y = 120
    linha_largura = 200
    x_inicio = (largura - linha_largura) / 2
    x_fim = x_inicio + linha_largura

    c.line(x_inicio, assinatura_y, x_fim, assinatura_y)
    c.setFont("Helvetica", 12)
    c.drawCentredString(largura / 2, assinatura_y - 15, "Assinatura")

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, download_name=f"comprovante_{pagamento_id}.pdf", as_attachment=True)


# Inicializar DB
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    # Para usar na web
    #app.run(debug=True, port=5002)
