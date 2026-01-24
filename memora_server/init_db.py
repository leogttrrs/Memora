from core.database import get_connection

def criar_tabelas():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("--- Iniciando Setup do Banco de Dados ---")

        # 1. Cria a tabela Filmes (se não existir)
        print("Verificando tabela 'filmes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filmes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                nota INT CHECK (nota >= 0 AND nota <= 10),
                assistido BOOLEAN DEFAULT FALSE
            );
        """)

        # 2. Adiciona colunas novas de forma segura (só adiciona se não existir)
        # O PostgreSQL permite "ADD COLUMN IF NOT EXISTS"
        print("Atualizando colunas de 'filmes'...")
        cursor.execute("ALTER TABLE filmes ADD COLUMN IF NOT EXISTS imagem_capa VARCHAR(255);")
        cursor.execute("ALTER TABLE filmes ADD COLUMN IF NOT EXISTS comentario TEXT;")

        # 3. Cria a tabela Fotos (CORRIGIDA)
        # Trocamos 'INT AUTO_INCREMENT' por 'SERIAL'
        # Trocamos 'DATETIME' por 'TIMESTAMP' (padrão do Postgres)
        print("Verificando tabela 'fotos_filme'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fotos_filme (
                id SERIAL PRIMARY KEY,
                filme_id INT NOT NULL,
                caminho_foto VARCHAR(255) NOT NULL,
                data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (filme_id) REFERENCES filmes(id) ON DELETE CASCADE
            );
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Sucesso! Todas as tabelas foram criadas/atualizadas.")

    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")

if __name__ == "__main__":
    criar_tabelas()