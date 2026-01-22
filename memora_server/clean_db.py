from core.database import get_connection


def remover_filmes():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS filmes")

        # Opção B: (Se quiser zerar tudo de uma vez)
        # cursor.execute("DELETE FROM filmes")

        conn.commit()
        linhas_afetadas = cursor.rowcount

        cursor.close()
        conn.close()

        if linhas_afetadas > 0:
            print(f"Sucesso! {linhas_afetadas} filme(s) removido(s).")
        else:
            print("Nenhum filme encontrado para remover.")

    except Exception as e:
        print(f"Erro ao limpar banco: {e}")


if __name__ == "__main__":
    remover_filmes()