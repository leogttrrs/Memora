from core.database import get_connection

def apagar_tudo():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("💣 Iniciando destruição das tabelas...")

        # O comando CASCADE garante que, se existirem dependências, elas somem junto.
        # Estamos apagando as duas tabelas de uma vez.
        cursor.execute("DROP TABLE IF EXISTS fotos_filme, filmes CASCADE;")

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Sucesso! As tabelas 'filmes' e 'fotos_filme' foram apagadas do mapa.")
        print("Agora você precisa rodar o script de criar tabelas novamente para usar o sistema.")

    except Exception as e:
        print(f"❌ Erro ao apagar tabelas: {e}")


if __name__ == "__main__":
    # Adicionei uma confirmação de segurança pra você não rodar sem querer
    confirmacao = input("Tem certeza que quer apagar TODO o banco de dados? (s/n): ")
    if confirmacao.lower() == 's':
        apagar_tudo()
    else:
        print("Operação cancelada.")