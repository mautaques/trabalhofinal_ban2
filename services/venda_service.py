"""Serviço de negócio para as entidades Venda e ItemVenda."""

from sqlalchemy import String, or_
from sqlalchemy.orm import joinedload

from database import get_session
from models.cliente import Cliente
from models.venda import ItemVenda, Venda


class VendaService:
    """CRUD para vendas e seus itens."""

    # ── Venda ────────────────────────────────────────────────────────────

    @staticmethod
    def listar_todos():
        """Retorna todas as vendas com filial, vendedor e cliente carregados."""
        with get_session() as session:
            return (
                session.query(Venda)
                .options(
                    joinedload(Venda.filial),
                    joinedload(Venda.vendedor),
                    joinedload(Venda.cliente),
                )
                .order_by(Venda.id_venda.desc())
                .all()
            )

    @staticmethod
    def buscar(termo: str):
        """Busca vendas por cupom fiscal ou nome do cliente."""
        with get_session() as session:
            return (
                session.query(Venda)
                .options(
                    joinedload(Venda.filial),
                    joinedload(Venda.vendedor),
                    joinedload(Venda.cliente),
                )
                .join(Venda.cliente)
                .filter(
                    or_(
                        Venda.cupom_fiscal.cast(String).ilike(f"%{termo}%"),
                        Cliente.nome.ilike(f"%{termo}%"),
                    )
                )
                .order_by(Venda.id_venda.desc())
                .all()
            )

    @staticmethod
    def criar(id_filial, id_vendedor, id_cliente, cupom_fiscal, forma_pagamento):
        """Cria uma nova venda (sem itens inicialmente)."""
        if not id_filial or not id_vendedor or not id_cliente:
            raise ValueError("Filial, vendedor e cliente são obrigatórios.")
        if not cupom_fiscal:
            raise ValueError("Cupom fiscal é obrigatório.")

        with get_session() as session:
            existente = (
                session.query(Venda).filter_by(cupom_fiscal=cupom_fiscal).first()
            )
            if existente:
                raise ValueError(f"Cupom fiscal '{cupom_fiscal}' já existe.")

            venda = Venda(
                id_filial=id_filial,
                id_vendedor=id_vendedor,
                id_cliente=id_cliente,
                cupom_fiscal=int(cupom_fiscal),
                forma_pagamento=forma_pagamento,
                valor_total=0,
            )
            session.add(venda)
            session.commit()
            session.refresh(venda)
            return venda

    @staticmethod
    def excluir(id_venda: int):
        """Exclui uma venda e todos os seus itens."""
        with get_session() as session:
            venda = session.get(Venda, id_venda)
            if not venda:
                raise ValueError("Venda não encontrada.")
            session.query(ItemVenda).filter_by(id_venda=id_venda).delete()
            session.delete(venda)
            session.commit()

    # ── Itens da Venda ───────────────────────────────────────────────────

    @staticmethod
    def buscar_itens(id_venda: int):
        """Retorna os itens de uma venda com os produtos carregados."""
        with get_session() as session:
            return (
                session.query(ItemVenda)
                .options(joinedload(ItemVenda.produto))
                .filter_by(id_venda=id_venda)
                .all()
            )

    @staticmethod
    def adicionar_item(id_venda, id_produto, quantidade, preco_unitario, desconto=None):
        """Adiciona um item à venda e recalcula o valor total."""
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero.")
        if preco_unitario <= 0:
            raise ValueError("Preço unitário deve ser maior que zero.")

        with get_session() as session:
            item = ItemVenda(
                id_venda=id_venda,
                id_produto=id_produto,
                quantidade=int(quantidade),
                preco_unitario=preco_unitario,
                desconto=desconto,
            )
            session.add(item)
            session.flush()

            # Recalcula valor_total da venda
            VendaService._recalcular_total(session, id_venda)
            session.commit()
            return item

    @staticmethod
    def remover_item(id_item_venda: int):
        """Remove um item da venda e recalcula o valor total."""
        with get_session() as session:
            item = session.get(ItemVenda, id_item_venda)
            if not item:
                raise ValueError("Item não encontrado.")
            id_venda = item.id_venda
            session.delete(item)
            session.flush()

            VendaService._recalcular_total(session, id_venda)
            session.commit()

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _recalcular_total(session, id_venda: int):
        """Recalcula e atualiza o valor_total de uma venda."""
        venda = session.get(Venda, id_venda)
        itens = session.query(ItemVenda).filter_by(id_venda=id_venda).all()
        total = sum(
            (i.quantidade * i.preco_unitario)
            - (i.quantidade * i.preco_unitario * (i.desconto or 0))
            for i in itens
        )
        venda.valor_total = total
