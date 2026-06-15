"""Configuração de conexão com o PostgreSQL via SQLAlchemy.

As credenciais são lidas de variáveis de ambiente (com valores padrão para
desenvolvimento local), evitando deixar a senha escrita no código-fonte.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from urllib.parse import quote_plus

# --- Credenciais ---------------------------------------------------------
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "guilherme") #aqui altera a senha
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "farmacia")

DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)

# psycopg 3 usa o dialeto "postgresql+psycopg"
DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD_ENCODED}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# --- Engine e sessão -----------------------------------------------------
# echo=True imprime o SQL gerado no console (útil durante o desenvolvimento).
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# Fábrica de sessões: use SessionLocal() para abrir uma sessão de trabalho.
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base para os modelos (tabelas) do projeto."""


def get_session():
    """Abre uma nova sessão do banco de dados.

    Exemplo de uso:
        with get_session() as session:
            session.add(produto)
            session.commit()
    """
    return SessionLocal()


def test_connection() -> bool:
    """ Verifica se a conexão com o banco está funcionando. """
    from sqlalchemy import text

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"Falha ao conectar no PostgreSQL: {exc}")
        return False


if __name__ == "__main__":
    if test_connection():
        print("Conexão com o PostgreSQL OK!")
