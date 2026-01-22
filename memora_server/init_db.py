from core.database import get_connection


def criar_tabelas():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("Criando tabela 'Filmes' ...")

        filmes_teste = [
            "A Origem", "Matrix", "O Poderoso Chefão", "Cidade de Deus",
            "Clube da Luta", "Pulp Fiction", "O Senhor dos Anéis", "Vingadores: Ultimato",
            "Parasita", "A Viagem de Chihiro", "Gladiador", "Titanic",
            "Avatar", "Star Wars: Uma Nova Esperança", "Jurassic Park",
            "O Rei Leão", "Coringa", "Homem-Aranha", "De Volta para o Futuro",
            "Central do Brasil", "Tropa de Elite", "O Auto da Compadecida"
        ]

        # 1. Cria a tabela
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filmes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                nota INT CHECK (nota >= 0 AND nota <= 10),
                assistido BOOLEAN DEFAULT FALSE
            );
        """)

        # 2. Verifica se está vazia
        cursor.execute("SELECT count(*) FROM filmes")
        count = cursor.fetchone()[0]

        if count == 0:
            print("Populando banco de dados...")

            # --- CORREÇÃO 1: Faltava um %s aqui ---
            # INSERT INTO colunas (1, 2) VALUES (1, 2)
            for filme in filmes_teste:
                cursor.execute(
                    "INSERT INTO filmes (nome, assistido) VALUES (%s, %s)",
                    (filme, False)
                )

            # --- CORREÇÃO 2: Faltava um %s aqui também ---
            # INSERT INTO colunas (1, 2, 3) VALUES (1, 2, 3)
            filmes_com_nota = [
                ('Vingadores', 9, True),
                ('O Lagosta', 3, True),
                ('Crepusculo', 6, True),
                # ... adicionei uma lista pra ficar mais limpo que repetir o codigo ...
            ]

            for f in filmes_com_nota:
                cursor.execute(
                    "INSERT INTO filmes (nome, nota, assistido) VALUES (%s, %s, %s)",
                    (f[0], f[1], f[2])
                )

            # Se quiser repetir Vingadores várias vezes como estava no seu código:
            for _ in range(10):
                cursor.execute(
                    "INSERT INTO filmes (nome, nota, assistido) VALUES (%s, %s, %s)",
                    ('Vingadores', 9, True)
                )

        else:
            print(f"O banco já tem {count} filmes. Pulei a inserção.")

        conn.commit()
        cursor.close()
        conn.close()
        print("Sucesso! Tabelas criadas e filmes inseridos.")

    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")


if __name__ == "__main__":
    criar_tabelas()