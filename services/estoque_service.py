"""Serviço de negócio para consulta de Estoque.

Expõe o estoque por produto/filial/lote junto de um indicador de situação:
CRÍTICO quando a quantidade está no nível mínimo (ou abaixo), caso contrário OK.
"""

from sqlalchemy import text

from database import get_session

# Consulta base reaproveitada por listar_todos() e buscar(). A coluna "situacao"
# é calculada no banco: CRÍTICO quando quantidade <= estoque_minimo.
_BASE_QUERY = (
    "SELECT e.id_estoque, p.nome_produto, "
    "       fi.nome_fantasia AS filial, l.numero_lote, l.data_validade, "
    "       e.quantidade, e.estoque_minimo, e.estoque_maximo, "
    "       (e.quantidade <= e.estoque_minimo) AS critico "
    "FROM estoque e "
    "JOIN produto p ON e.id_produto = p.id_produto "
    "JOIN filial fi ON e.id_filial = fi.id_filial "
    "JOIN lote l ON e.id_lote = l.id_lote "
)


class EstoqueService:
    """Consultas sobre o estoque (somente leitura)."""

    @staticmethod
    def listar_todos():
        """Retorna todo o estoque, com os críticos primeiro."""
        with get_session() as session:
            return session.execute(text(
                _BASE_QUERY
                + "ORDER BY critico DESC, p.nome_produto"
            )).fetchall()

    @staticmethod
    def buscar(termo: str):
        """Busca o estoque por produto ou filial."""
        with get_session() as session:
            return session.execute(
                text(
                    _BASE_QUERY
                    + "WHERE p.nome_produto ILIKE :termo "
                    "   OR fi.nome_fantasia ILIKE :termo "
                    "ORDER BY critico DESC, p.nome_produto"
                ),
                {"termo": f"%{termo}%"},
            ).fetchall()

    @staticmethod
    def contar_criticos() -> int:
        """Conta quantos itens de estoque estão em nível crítico."""
        with get_session() as session:
            return session.execute(text(
                "SELECT COUNT(*) FROM estoque "
                "WHERE quantidade <= estoque_minimo"
            )).scalar() or 0
