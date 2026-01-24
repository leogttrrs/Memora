from core.database import get_connection


def criar_tabelas():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("Criando tabela 'Filmes' ...")

        # 1. Cria a tabela
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filmes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                nota INT CHECK (nota >= 0 AND nota <= 10),
                assistido BOOLEAN DEFAULT FALSE
            );
        """)

        cursor.execute("ALTER TABLE filmes ADD COLUMN imagem_capa VARCHAR(255);")

        cursor.execute("ALTER TABLE filmes ADD COLUMN comentario TEXT;")

        conn.commit()
        cursor.close()
        conn.close()
        print("Sucesso! Tabelas criadas e filmes inseridos.")

    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")


if __name__ == "__main__":
    criar_tabelas()