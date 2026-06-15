"""Serviço de negócio para Devoluções."""

import json

from sqlalchemy import text

from database import get_session


class DevolucaoService:
    """Operações sobre devoluções, usando a função SQL devolver_produtos()."""

    @staticmethod
    def listar_todos():
        """Retorna todas as devoluções com dados da venda e cliente."""
        with get_session() as session:
            rows = session.execute(text(
                "SELECT d.id_devolucao, d.id_venda, v.cupom_fiscal, "
                "       c.nome AS cliente, d.data_devolucao, d.motivo, d.tipo "
                "FROM devolucao d "
                "JOIN venda v ON d.id_venda = v.id_venda "
                "JOIN cliente c ON v.id_cliente = c.id_cliente "
                "ORDER BY d.id_devolucao DESC"
            )).fetchall()
            return rows

    @staticmethod
    def buscar(termo: str):
        """Busca devoluções por cupom fiscal, cliente ou motivo."""
        with get_session() as session:
            rows = session.execute(
                text(
                    "SELECT d.id_devolucao, d.id_venda, v.cupom_fiscal, "
                    "       c.nome AS cliente, d.data_devolucao, d.motivo, d.tipo "
                    "FROM devolucao d "
                    "JOIN venda v ON d.id_venda = v.id_venda "
                    "JOIN cliente c ON v.id_cliente = c.id_cliente "
                    "WHERE v.cupom_fiscal::TEXT ILIKE :termo "
                    "   OR c.nome ILIKE :termo "
                    "   OR d.motivo ILIKE :termo "
                    "ORDER BY d.id_devolucao DESC"
                ),
                {"termo": f"%{termo}%"},
            ).fetchall()
            return rows

    @staticmethod
    def buscar_itens(id_devolucao: int):
        """Retorna os itens de uma devolução."""
        with get_session() as session:
            rows = session.execute(
                text(
                    "SELECT id.id_item_devolucao, p.nome_produto, id.quantidade "
                    "FROM item_devolucao id "
                    "JOIN produto p ON id.id_produto = p.id_produto "
                    "WHERE id.id_devolucao = :id_dev "
                    "ORDER BY id.id_item_devolucao"
                ),
                {"id_dev": id_devolucao},
            ).fetchall()
            return rows

    @staticmethod
    def buscar_itens_venda(id_venda: int):
        """Retorna os itens de uma venda para seleção na devolução."""
        with get_session() as session:
            rows = session.execute(
                text(
                    "SELECT iv.id_item_venda, p.id_produto, p.nome_produto, "
                    "       iv.quantidade, iv.preco_unitario "
                    "FROM item_venda iv "
                    "JOIN produto p ON iv.id_produto = p.id_produto "
                    "WHERE iv.id_venda = :id_venda "
                    "ORDER BY iv.id_item_venda"
                ),
                {"id_venda": id_venda},
            ).fetchall()
            return rows

    @staticmethod
    def devolver(id_venda, itens, motivo, tipo):
        """Chama a função SQL devolver_produtos()."""
        itens_json = json.dumps(itens)
        with get_session() as session:
            result = session.execute(
                text(
                    "SELECT devolver_produtos(:id_venda, :itens::jsonb, :motivo, :tipo)"
                ),
                {
                    "id_venda": id_venda,
                    "itens": itens_json,
                    "motivo": motivo,
                    "tipo": tipo,
                },
            ).scalar()
            session.commit()
            return result
