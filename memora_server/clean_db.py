from core.database import get_connection

def apagar_tudo():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("💣 Iniciando destruição TOTAL do banco...")

        cursor.execute("DROP SCHEMA public CASCADE;")
        cursor.execute("CREATE SCHEMA public;")

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Banco completamente limpo.")
        print("Agora rode o script de criação das tabelas novamente.")

    except Exception as e:
        print(f"❌ Erro ao apagar banco: {e}")


if __name__ == "__main__":
    confirmacao = input("Tem certeza que quer apagar TODO o banco de dados? (s/n): ")
    if confirmacao.lower() == 's':
        apagar_tudo()
    else:
        print("Operação cancelada.")