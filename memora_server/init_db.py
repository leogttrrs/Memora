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
                nota INT CHECK (nota >= 1 AND nota <= 10),
                assistido BOOLEAN DEFAULT FALSE
            );
        """)

        print("Verificando tabela 'series'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS series (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                nota_geral INT CHECK (nota_geral >= 1 AND nota_geral <= 10) DEFAULT 5,
                assistido_completo BOOLEAN DEFAULT FALSE,
                imagem_capa VARCHAR(255),
                comentario TEXT -- <--- TIREI A VÍRGULA DAQUI
            );
        """)

        print("Verificando tabela 'temporadas'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS temporadas (
                id SERIAL PRIMARY KEY,
                serie_id INT NOT NULL,
                numero_temporada INT NOT NULL,
                nota INT CHECK (nota >= 0 AND nota <= 10),
                assistido BOOLEAN DEFAULT FALSE,
                comentario TEXT,
                FOREIGN KEY (serie_id) REFERENCES series(id) ON DELETE CASCADE,
                UNIQUE (serie_id, numero_temporada) -- <--- SUGESTÃO: IMPEDE DUPLICIDADE
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

        print("Verificando tabela 'fotos_serie'...")
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS fotos_serie (
                        id SERIAL PRIMARY KEY,
                        serie_id INT NOT NULL,
                        caminho_foto VARCHAR(255) NOT NULL,
                        data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (serie_id) REFERENCES series(id) ON DELETE CASCADE
                    );
                """)

        print("Verificando tabela 'fotos_temporada'...")
        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS fotos_temporada (
                                id SERIAL PRIMARY KEY,
                                temporada_id INT NOT NULL,
                                caminho_foto VARCHAR(255) NOT NULL,
                                data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (temporada_id) REFERENCES temporadas(id) ON DELETE CASCADE
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