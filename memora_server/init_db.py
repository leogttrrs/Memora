from core.database import get_connection

def criar_tabelas():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("--- Iniciando Setup do Banco de Dados ---")

        # ==========================================
        # FASE 1: USUÁRIOS E CÍRCULOS (MULTI-TENANCY)
        # ==========================================
        print("Verificando tabela 'usuarios'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                nome VARCHAR(255) NOT NULL,
                foto_url VARCHAR(255),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        print("Verificando tabela 'circulos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS circulos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                criador_id INT NOT NULL,
                emoji VARCHAR(10) DEFAULT '🪐',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (criador_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
        """)

        print("Verificanto tabela 'Convites' ...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS convites (
                id SERIAL PRIMARY KEY,
                circulo_id INT NOT NULL,
                email_convidado VARCHAR(255) NOT NULL,
                data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(circulo_id, email_convidado),
                FOREIGN KEY (circulo_id) REFERENCES circulos(id) ON DELETE CASCADE
            );
        """)

        print("Verificando tabela 'membros_circulo'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS membros_circulo (
                circulo_id INT NOT NULL,
                usuario_id INT NOT NULL,
                papel VARCHAR(50) DEFAULT 'membro', -- ex: 'admin', 'membro'
                data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (circulo_id, usuario_id),
                FOREIGN KEY (circulo_id) REFERENCES circulos(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
        """)

        # ==========================================
        # FASE 2: TABELAS PRINCIPAIS (AGORA COM circulo_id)
        # ==========================================
        print("Verificando tabela 'filmes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filmes (
                id SERIAL PRIMARY KEY,
                circulo_id INT NOT NULL,
                nome VARCHAR(255) NOT NULL,
                nota INT CHECK (nota >= 1 AND nota <= 10),
                assistido BOOLEAN DEFAULT FALSE,
                imagem_capa VARCHAR(255),
                comentario TEXT,
                FOREIGN KEY (circulo_id) REFERENCES circulos(id) ON DELETE CASCADE
            );
        """)

        print("Verificando tabela 'jogos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jogos (
                id SERIAL PRIMARY KEY,
                circulo_id INT NOT NULL,
                nome VARCHAR(255) NOT NULL,
                nota INT CHECK (nota >= 1 AND nota <= 10),
                finalizado BOOLEAN DEFAULT FALSE,
                imagem_capa VARCHAR(255),
                comentario TEXT,
                FOREIGN KEY (circulo_id) REFERENCES circulos(id) ON DELETE CASCADE
            );
        """)

        print("Verificando tabela 'series'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS series (
                id SERIAL PRIMARY KEY,
                circulo_id INT NOT NULL,
                nome VARCHAR(255) NOT NULL,
                nota_geral INT CHECK (nota_geral >= 1 AND nota_geral <= 10),
                assistido_completo BOOLEAN DEFAULT FALSE,
                imagem_capa VARCHAR(255),
                comentario TEXT,
                FOREIGN KEY (circulo_id) REFERENCES circulos(id) ON DELETE CASCADE
            );
        """)

        print("Verificando tabela 'receitas'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS receitas (
                id SERIAL PRIMARY KEY,
                circulo_id INT NOT NULL,
                nome VARCHAR(255) NOT NULL,
                nota INT CHECK (nota >= 1 AND nota <= 10),
                provada BOOLEAN DEFAULT FALSE,
                imagem_capa VARCHAR(255),
                ingredientes TEXT,
                modo_preparo TEXT,
                comentario TEXT,
                FOREIGN KEY (circulo_id) REFERENCES circulos(id) ON DELETE CASCADE
            );
        """)

        print("Verificando tabela 'viagens'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS viagens (
                id SERIAL PRIMARY KEY,
                circulo_id INT NOT NULL,
                nome VARCHAR(255) NOT NULL,
                nota INT CHECK (nota >= 1 AND nota <= 10),
                feita BOOLEAN DEFAULT FALSE,
                imagem_capa VARCHAR(255),
                comentario TEXT,
                FOREIGN KEY (circulo_id) REFERENCES circulos(id) ON DELETE CASCADE
            );
        """)

        # ==========================================
        # FASE 3: TABELAS FILHAS (Aninhadas)
        # ==========================================
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
                UNIQUE (serie_id, numero_temporada)
            );
        """)

        print("Verificando tabela 'cidades_x_viagem'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cidades_x_viagem (
                id SERIAL PRIMARY KEY,
                viagem_id INT NOT NULL,
                nome_cidade VARCHAR NOT NULL,
                visitada BOOLEAN DEFAULT FALSE,
                nota INT CHECK (nota >= 0 AND nota <= 10),
                comentario TEXT,
                data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (viagem_id) REFERENCES viagens(id) ON DELETE CASCADE
            );
        """)

        # ==========================================
        # FASE 4: TABELAS DE FOTOS
        # ==========================================
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

        print("Verificando tabela 'fotos_receita'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fotos_receita (
                id SERIAL PRIMARY KEY,
                receita_id INT NOT NULL,
                caminho_foto VARCHAR(255) NOT NULL,
                data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (receita_id) REFERENCES receitas(id) ON DELETE CASCADE
            );
        """)

        print("Verificando tabela 'fotos_viagem'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fotos_viagem (
                id SERIAL PRIMARY KEY,
                viagem_id INT NOT NULL,
                caminho_foto VARCHAR(255) NOT NULL,
                data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (viagem_id) REFERENCES viagens(id) ON DELETE CASCADE
            );
        """)

        print("Verificando tabela 'fotos_cidade'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fotos_cidade (
                id SERIAL PRIMARY KEY,
                cidade_id INT NOT NULL,
                caminho_foto VARCHAR(255) NOT NULL,
                data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cidade_id) REFERENCES cidades_x_viagem(id) ON DELETE CASCADE
            );
        """)

        print("Verificando tabela 'fotos_jogo'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fotos_jogo (
                id SERIAL PRIMARY KEY,
                jogo_id INT NOT NULL,
                caminho_foto VARCHAR(255) NOT NULL,
                data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (jogo_id) REFERENCES jogos(id) ON DELETE CASCADE
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