"""Serviço de negócio para consulta de Recebimentos.

Lista os produtos efetivamente recebidos: cada registro de `recebido` está ligado
a um pedido de reposição, que por sua vez tem vários itens (produtos). A consulta
junta tudo para mostrar, por produto, o que já entrou no estoque.
"""

from sqlalchemy import text

from database import get_session

# Consulta base reaproveitada por listar_todos() e buscar().
_BASE_QUERY = (
    "SELECT r.id_recebido, re.numero_pedido, p.nome_produto, "
    "       ir.quantidade, f.nome_fantasia AS fornecedor, "
    "       fi.nome_fantasia AS filial, r.data, "
    "       r.divergência AS divergencia "
    "FROM recebido r "
    "JOIN reposicao_estoque re ON r.id_reposicao = re.id_reposicao "
    "JOIN item_reposicao ir ON ir.id_reposicao = re.id_reposicao "
    "JOIN produto p ON ir.id_produto = p.id_produto "
    "JOIN fornecedor f ON re.id_fornecedor = f.id_fornecedor "
    "JOIN filial fi ON re.id_filial_destino = fi.id_filial "
)


class RecebidoService:
    """Consultas sobre produtos recebidos (somente leitura)."""

    @staticmethod
    def listar_todos():
        """Retorna todos os produtos recebidos, mais recentes primeiro."""
        with get_session() as session:
            return session.execute(text(
                _BASE_QUERY
                + "ORDER BY r.data DESC, p.nome_produto"
            )).fetchall()

    @staticmethod
    def buscar(termo: str):
        """Busca por produto, fornecedor, filial ou número do pedido."""
        with get_session() as session:
            return session.execute(
                text(
                    _BASE_QUERY
                    + "WHERE p.nome_produto ILIKE :termo "
                    "   OR f.nome_fantasia ILIKE :termo "
                    "   OR fi.nome_fantasia ILIKE :termo "
                    "   OR re.numero_pedido::TEXT ILIKE :termo "
                    "ORDER BY r.data DESC, p.nome_produto"
                ),
                {"termo": f"%{termo}%"},
            ).fetchall()
