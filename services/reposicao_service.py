"""Serviço de negócio para Reposição de Estoque."""

import json

from sqlalchemy import String, text, or_
from sqlalchemy.orm import joinedload

from database import get_session


class ReposicaoService:
    """Operações sobre pedidos de reposição, usando as funções SQL do banco."""

    @staticmethod
    def listar_todos():
        """Retorna todos os pedidos de reposição com fornecedor e filial."""
        with get_session() as session:
            rows = session.execute(text(
                "SELECT r.id_reposicao, r.numero_pedido, r.data_pedido, r.status, "
                "       r.valor_total, f.nome_fantasia AS fornecedor, "
                "       fi.nome_fantasia AS filial "
                "FROM reposicao_estoque r "
                "JOIN fornecedor f ON r.id_fornecedor = f.id_fornecedor "
                "JOIN filial fi ON r.id_filial_destino = fi.id_filial "
                "ORDER BY r.id_reposicao DESC"
            )).fetchall()
            return rows

    @staticmethod
    def buscar(termo: str):
        """Busca reposições por número de pedido ou fornecedor."""
        with get_session() as session:
            rows = session.execute(
                text(
                    "SELECT r.id_reposicao, r.numero_pedido, r.data_pedido, r.status, "
                    "       r.valor_total, f.nome_fantasia AS fornecedor, "
                    "       fi.nome_fantasia AS filial "
                    "FROM reposicao_estoque r "
                    "JOIN fornecedor f ON r.id_fornecedor = f.id_fornecedor "
                    "JOIN filial fi ON r.id_filial_destino = fi.id_filial "
                    "WHERE r.numero_pedido::TEXT ILIKE :termo "
                    "   OR f.nome_fantasia ILIKE :termo "
                    "ORDER BY r.id_reposicao DESC"
                ),
                {"termo": f"%{termo}%"},
            ).fetchall()
            return rows

    @staticmethod
    def buscar_itens(id_reposicao: int):
        """Retorna os itens de um pedido de reposição."""
        with get_session() as session:
            rows = session.execute(
                text(
                    "SELECT ir.id_item_reposicao, p.nome_produto, ir.quantidade, "
                    "       ir.valor_unitario, ir.valor_total, l.numero_lote "
                    "FROM item_reposicao ir "
                    "JOIN produto p ON ir.id_produto = p.id_produto "
                    "JOIN lote l ON ir.id_lote = l.id_lote "
                    "WHERE ir.id_reposicao = :id_rep "
                    "ORDER BY ir.id_item_reposicao"
                ),
                {"id_rep": id_reposicao},
            ).fetchall()
            return rows

    @staticmethod
    def insere_pedido(id_fornecedor, id_filial_destino, itens):
        """Chama a função SQL insere_pedido_reposicao().

        O número do pedido é gerado automaticamente pelo banco, assim como o
        lote de cada item — resolvido a partir do produto (cada item carrega
        apenas id_produto, quantidade e valor_unitario).
        """
        itens_json = json.dumps(itens)
        with get_session() as session:
            result = session.execute(
                text(
                    "SELECT insere_pedido_reposicao("
                    "  :fornecedor, :filial, :itens::jsonb"
                    ")"
                ),
                {
                    "fornecedor": id_fornecedor,
                    "filial": id_filial_destino,
                    "itens": itens_json,
                },
            ).scalar()
            session.commit()
            return result

    @staticmethod
    def receber(id_reposicao, quantidade, divergencia=None):
        """Chama a função SQL recebe_reposicao()."""
        with get_session() as session:
            result = session.execute(
                text(
                    "SELECT recebe_reposicao(:id_rep, :qtd, :div)"
                ),
                {
                    "id_rep": id_reposicao,
                    "qtd": quantidade,
                    "div": divergencia,
                },
            ).scalar()
            session.commit()
            return result
