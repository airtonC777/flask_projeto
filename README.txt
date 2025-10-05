# 💻 Sistema de Pagamentos - Flask

Aplicação web em **Flask** para gerir pagamentos de clubes (Aventureiros, Desbravadores, Embaixadores, JA e Líderes).
Permite cadastrar pagamentos mensais, listar registros e gerar comprovantes em PDF com logo e assinatura.

---

## 🚀 Como rodar localmente

### 1. Clonar o repositório
git clone https://github.com/SEU_USUARIO/flask_projeto.git
cd flask_projeto

### 2. Criar ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

### 3. Instalar dependências
pip install -r requirements.txt

### 4. Executar aplicação
python app.py

Abrir no navegador: 👉 http://127.0.0.1:5000

---

## ☁️ Deploy no GitHub + Render

### 1. Subir para GitHub
No diretório do projeto:
git init
git add .
git commit -m "primeiro deploy"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/flask_projeto.git
git push -u origin main

---

### 2. Configuração no Render
1. Criar conta em https://render.com (login com GitHub).
2. Dashboard → New → Web Service.
3. Selecionar o repositório flask_projeto.
4. Configurar:
   - Name: meu-clube-pagamentos
   - Branch: main
   - Environment: Python 3
   - Build Command:
     pip install -r requirements.txt
   - Start Command:
     gunicorn app:app

5. Clicar em Create Web Service / Deploy Web Service.

---

### 3. Aceder
Após o deploy, Render fornece um link do tipo:
https://meu-clube-pagamentos.onrender.com

Esse será o endereço público da tua aplicação 🎉

---

## 📌 Notas importantes

- O projeto usa SQLite (pagamentos.db) por padrão.
- Em produção (Render), o SQLite pode ser apagado quando o container reinicia.
- Para uso sério, recomenda-se migrar para PostgreSQL gratuito do Render.
- Caso uses PostgreSQL, adapta o app.py para ler a variável de ambiente DATABASE_URL.

---

## 🛠️ Tecnologias usadas

- Python + Flask
- Flask-SQLAlchemy (ORM)
- Flask-Login (autenticação)
- Bootstrap (frontend)
- ReportLab (geração de PDF)
- GitHub (repositório)
- Render (deploy)

---

## ✨ Autor

Projeto desenvolvido por **Airton Ngola** 🚀
