import sqlite3

# Caminho do banco de dados
DB_PATH = "pagamentos.db"

def criar_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cria a tabela pagamento, se ainda não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clube TEXT NOT NULL,
            igreja TEXT NOT NULL,
            regiao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            ano INTEGER NOT NULL,
            total REAL,
            janeiro REAL,
            fevereiro REAL,
            marco REAL,
            abril REAL,
            maio REAL,
            junho REAL,
            julho REAL,
            agosto REAL,
            setembro REAL,
            outubro REAL,
            novembro REAL,
            dezembro REAL
        );
    """)

    conn.commit()
    conn.close()
    print("✅ Banco de dados e tabela 'pagamento' criados com sucesso!")

if __name__ == "__main__":
    print("🔄 Verificando estrutura do banco de dados...")
    criar_banco()
    print("🏁 Concluído!")
