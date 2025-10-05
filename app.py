import os
import io
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# --- App config ---
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# DATABASE URL: use DATABASE_URL when available (Render/Postgres), otherwise sqlite file
db_url = os.getenv("DATABASE_URL", "sqlite:///pagamentos.db")
# SQLAlchemy expects "postgresql://" rather than "postgres://"
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- DB init ---
db = SQLAlchemy(app)

# --- Login manager ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# --- Models ---
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clube = db.Column(db.String(100))
    igreja = db.Column(db.String(100))
    regiao = db.Column(db.String(100))
    categoria = db.Column(db.String(100))
    ano = db.Column(db.Integer, nullable=False)            # NOVO CAMPO
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

# --- Helpers ---
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

def soma_meses_form(request_form):
    """Soma os valores dos meses recebidos do form. Retorna string com 2 decimais."""
    soma = 0.0
    meses = ["janeiro","fevereiro","marco","abril","maio","junho",
             "julho","agosto","setembro","outubro","novembro","dezembro"]
    for m in meses:
        v = request_form.get(m, "")
        # aceita '', '0', '1000', '1000.50'
        try:
            if v is None or v == "":
                val = 0.0
            else:
                # remove vírgulas e espaços, admite decimal com ponto ou vírgula
                v_clean = str(v).replace(",", ".").strip()
                val = float(v_clean) if v_clean != "" else 0.0
        except ValueError:
            val = 0.0
        soma += val
    return f"{soma:.2f}"

def format_currency_str(s):
    """Formata string numérica para exibição (ex: '5000.00' -> '5.000,00')"""
    try:
        v = float(str(s).replace(",", "."))
    except:
        return s
    # usar separador mil e vírgula decimal (pt style)
    inteiro = int(v)
    frac = int(round((v - inteiro) * 100))
    inteiro_fmt = f"{inteiro:,}".replace(",", ".")
    return f"{inteiro_fmt},{frac:02d}"

# --- Routes: registro / login / logout ---

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        if not nome or not email or not senha:
            flash("Preencha todos os campos.", "danger")
            return redirect(url_for("registro"))
        if not senha_forte(senha):
            flash("A senha deve ter pelo menos 8 caracteres, incluindo maiúscula, minúscula, número e símbolo.", "danger")
            return redirect(url_for("registro"))
        if Usuario.query.filter_by(email=email).first():
            flash("Email já registrado.", "danger")
            return redirect(url_for("registro"))

        novo = Usuario(nome=nome, email=email, senha=generate_password_hash(senha))
        db.session.add(novo)
        db.session.commit()
        flash("Usuário registrado com sucesso!", "success")
        return redirect(url_for("login"))
    return render_template("registro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("index"))
        flash("Credenciais inválidas.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout realizado.", "success")
    return redirect(url_for("login"))

# --- Index / Principal ---
@app.route("/")
@login_required
def index():
    return render_template("principal.html")

# --- Formulário ---
@app.route("/formulario", methods=["GET", "POST"])
@login_required
def formulario():
    if request.method == "POST":
        # Validações básicas + ano obrigatório e numérico
        clubes = request.form.get("clube", "").strip()
        igreja = request.form.get("igreja", "").strip()
        regiao = request.form.get("regiao", "").strip()
        categoria = request.form.get("categoria", "").strip()
        ano_raw = request.form.get("ano", "").strip()

        erros = []
        if not clubes:
            erros.append("O campo Clube é obrigatório.")
        if not igreja:
            erros.append("O campo Igreja é obrigatório.")
        if not regiao:
            erros.append("O campo Região é obrigatório.")
        if not categoria:
            erros.append("O campo Categoria é obrigatório.")
        if not ano_raw:
            erros.append("O campo Ano é obrigatório.")
        else:
            try:
                ano = int(ano_raw)
                if ano < 1900 or ano > 2100:
                    erros.append("O campo Ano deve ser um número válido (ex: 2025).")
            except ValueError:
                erros.append("O campo Ano deve ser um número inteiro.")

        # Se houver erros, mostra e retorna
        if erros:
            for e in erros:
                flash(e, "danger")
            # mantém categoria_header se veio pela query
            categoria_header = request.args.get("categoria", "")
            return render_template("formulario.html", categoria_header=categoria_header)

        # Calcula total pelo servidor (garante integridade)
        total_str = soma_meses_form(request.form)

        # Cria novo pagamento
        novo = Pagamento(
            clube=clubes,
            igreja=igreja,
            regiao=regiao,
            categoria=categoria,
            ano=int(ano_raw),
            total=total_str,
            janeiro=request.form.get("janeiro", ""),
            fevereiro=request.form.get("fevereiro", ""),
            marco=request.form.get("marco", ""),
            abril=request.form.get("abril", ""),
            maio=request.form.get("maio", ""),
            junho=request.form.get("junho", ""),
            julho=request.form.get("julho", ""),
            agosto=request.form.get("agosto", ""),
            setembro=request.form.get("setembro", ""),
            outubro=request.form.get("outubro", ""),
            novembro=request.form.get("novembro", ""),
            dezembro=request.form.get("dezembro", "")
        )
        db.session.add(novo)
        db.session.commit()
        flash("Pagamento cadastrado com sucesso!", "success")
        return redirect(url_for("resultado", pagamento_id=novo.id))

    categoria_header = request.args.get("categoria", "")
    return render_template("formulario.html", categoria_header=categoria_header)

# --- Resultado ---
@app.route("/resultado/<int:pagamento_id>")
@login_required
def resultado(pagamento_id):
    pagamento = Pagamento.query.get_or_404(pagamento_id)
    return render_template("resultado.html", dados=pagamento)

# --- Listar ---
@app.route("/listar")
@login_required
def listar():
    termo = request.args.get("busca", "")
    if termo:
        filtros = []
        termo_ilike = f"%{termo}%"
        filtros.extend([
            Pagamento.clube.ilike(termo_ilike),
            Pagamento.igreja.ilike(termo_ilike),
            Pagamento.regiao.ilike(termo_ilike),
            Pagamento.categoria.ilike(termo_ilike),
            Pagamento.janeiro.ilike(termo_ilike),
            Pagamento.fevereiro.ilike(termo_ilike),
            Pagamento.marco.ilike(termo_ilike),
            Pagamento.abril.ilike(termo_ilike),
            Pagamento.maio.ilike(termo_ilike),
            Pagamento.junho.ilike(termo_ilike),
            Pagamento.julho.ilike(termo_ilike),
            Pagamento.agosto.ilike(termo_ilike),
            Pagamento.setembro.ilike(termo_ilike),
            Pagamento.outubro.ilike(termo_ilike),
            Pagamento.novembro.ilike(termo_ilike),
            Pagamento.dezembro.ilike(termo_ilike),
            Pagamento.total.ilike(termo_ilike)
        ])
        pagamentos = Pagamento.query.filter(or_(*filtros)).all()
    else:
        pagamentos = Pagamento.query.order_by(Pagamento.id.desc()).all()
    return render_template("listar.html", pagamentos=pagamentos, termo=termo)

# --- Editar ---
@app.route("/editar/<int:pagamento_id>", methods=["GET", "POST"])
@login_required
def editar(pagamento_id):
    pagamento = Pagamento.query.get_or_404(pagamento_id)
    if request.method == "POST":
        clubes = request.form.get("clube", "").strip()
        igreja = request.form.get("igreja", "").strip()
        regiao = request.form.get("regiao", "").strip()
        categoria = request.form.get("categoria", "").strip()
        ano_raw = request.form.get("ano", "").strip()
        erros = []
        if not clubes:
            erros.append("O campo Clube é obrigatório.")
        if not igreja:
            erros.append("O campo Igreja é obrigatório.")
        if not regiao:
            erros.append("O campo Região é obrigatório.")
        if not categoria:
            erros.append("O campo Categoria é obrigatório.")
        if not ano_raw:
            erros.append("O campo Ano é obrigatório.")
        else:
            try:
                ano = int(ano_raw)
                if ano < 1900 or ano > 2100:
                    erros.append("O campo Ano deve ser um número válido (ex: 2025).")
            except ValueError:
                erros.append("O campo Ano deve ser um número inteiro.")
        if erros:
            for e in erros:
                flash(e, "danger")
            return render_template("editar.html", pagamento=pagamento)

        # Atualiza campos
        pagamento.clube = clubes
        pagamento.igreja = igreja
        pagamento.regiao = regiao
        pagamento.categoria = categoria
        pagamento.ano = int(ano_raw)
        pagamento.janeiro = request.form.get("janeiro", "")
        pagamento.fevereiro = request.form.get("fevereiro", "")
        pagamento.marco = request.form.get("marco", "")
        pagamento.abril = request.form.get("abril", "")
        pagamento.maio = request.form.get("maio", "")
        pagamento.junho = request.form.get("junho", "")
        pagamento.julho = request.form.get("julho", "")
        pagamento.agosto = request.form.get("agosto", "")
        pagamento.setembro = request.form.get("setembro", "")
        pagamento.outubro = request.form.get("outubro", "")
        pagamento.novembro = request.form.get("novembro", "")
        pagamento.dezembro = request.form.get("dezembro", "")
        # recalcula total
        pagamento.total = soma_meses_form(request.form)
        db.session.commit()
        flash("Pagamento atualizado com sucesso!", "success")
        return redirect(url_for("listar"))
    return render_template("editar.html", pagamento=pagamento)

# --- Excluir ---
@app.route("/excluir/<int:pagamento_id>")
@login_required
def excluir(pagamento_id):
    pagamento = Pagamento.query.get_or_404(pagamento_id)
    db.session.delete(pagamento)
    db.session.commit()
    flash("Pagamento excluído com sucesso!", "success")
    return redirect(url_for("listar"))

# --- Exportar Excel ---
@app.route("/exportar_excel")
@login_required
def exportar_excel():
    pagamentos = Pagamento.query.all()
    dados = []
    for p in pagamentos:
        dados.append({
            "ID": p.id,
            "Clube": p.clube,
            "Igreja": p.igreja,
            "Região": p.regiao,
            "Categoria": p.categoria,
            "Total": p.total,
            "Ano": p.ano,
            "Janeiro": p.janeiro,
            "Fevereiro": p.fevereiro,
            "Março": p.marco,
            "Abril": p.abril,
            "Maio": p.maio,
            "Junho": p.junho,
            "Julho": p.julho,
            "Agosto": p.agosto,
            "Setembro": p.setembro,
            "Outubro": p.outubro,
            "Novembro": p.novembro,
            "Dezembro": p.dezembro
        })
    df = pd.DataFrame(dados)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Pagamentos")
    output.seek(0)
    return send_file(output, download_name="pagamentos.xlsx", as_attachment=True)

# --- Comprovante PDF ---
@app.route("/comprovante/<int:pagamento_id>")
@login_required
def comprovante(pagamento_id):
    pagamento = Pagamento.query.get(pagamento_id)
    if not pagamento:
        abort(404)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    # Logo centralizado (se existir)
    logo_path = os.path.join(app.root_path, "static", "logo.png")
    try:
        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            logo_width, logo_height = 100, 100
            c.drawImage(logo, (largura - logo_width) / 2, altura - logo_height - 30,
                        width=logo_width, height=logo_height, mask="auto")
    except Exception as e:
        print("Erro ao carregar logo:", e)

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(largura / 2, altura - 160, "Comprovante de Pagamento")

    # Conteúdo
    c.setFont("Helvetica", 12)
    y = altura - 200

    if pagamento.clube and pagamento.clube.strip():
        c.drawString(80, y, f"Clube: {pagamento.clube}")
        y -= 20

    # Categoria e Ano na mesma linha formatada
    linha_cat_ano = f"Categoria: {pagamento.categoria} / Ano: {pagamento.ano}"
    c.drawString(80, y, linha_cat_ano)
    y -= 20

    if pagamento.igreja and pagamento.igreja.strip():
        c.drawString(80, y, f"Igreja: {pagamento.igreja}")
        y -= 20
    if pagamento.regiao and pagamento.regiao.strip():
        c.drawString(80, y, f"Região: {pagamento.regiao}")
        y -= 25

    # Meses (apenas os preenchidos)
    meses = [
        ("Janeiro", pagamento.janeiro),
        ("Fevereiro", pagamento.fevereiro),
        ("Março", pagamento.marco),
        ("Abril", pagamento.abril),
        ("Maio", pagamento.maio),
        ("Junho", pagamento.junho),
        ("Julho", pagamento.julho),
        ("Agosto", pagamento.agosto),
        ("Setembro", pagamento.setembro),
        ("Outubro", pagamento.outubro),
        ("Novembro", pagamento.novembro),
        ("Dezembro", pagamento.dezembro),
    ]
    for nome, valor in meses:
        if valor and str(valor).strip() != "":
            # formato simples
            c.drawString(80, y, f"{nome}: {valor}")
            y -= 18

    # Total
    if pagamento.total and str(pagamento.total).strip() != "":
        c.setFont("Helvetica-Bold", 12)
        c.drawString(80, y - 6, f"Total: {format_currency_str(pagamento.total)}")
        y -= 30

    # Data emissão
    c.setFont("Helvetica-Oblique", 10)
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.drawString(80, y - 10, f"Data de emissão: {agora}")

    # Assinatura centralizada
    assinatura_y = 90
    linha_largura = 200
    x_inicio = (largura - linha_largura) / 2
    x_fim = x_inicio + linha_largura
    c.line(x_inicio, assinatura_y, x_fim, assinatura_y)
    c.setFont("Helvetica", 12)
    c.drawCentredString(largura / 2, assinatura_y - 16, "Assinatura")

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, download_name=f"comprovante_{pagamento_id}.pdf", as_attachment=True)

# --- Inicialização DB e app run ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
