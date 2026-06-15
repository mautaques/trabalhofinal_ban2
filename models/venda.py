"""Modelos ORM para as tabelas *venda* e *item_venda*."""

import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Computed,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Venda(Base):
    __tablename__ = "venda"

    id_venda: Mapped[int] = mapped_column(primary_key=True)
    id_filial: Mapped[int] = mapped_column(
        ForeignKey("filial.id_filial"), nullable=False
    )
    id_vendedor: Mapped[int] = mapped_column(
        ForeignKey("vendedor.id_vendedor"), nullable=False
    )
    id_cliente: Mapped[int] = mapped_column(
        ForeignKey("cliente.id_cliente"), nullable=False
    )
    cupom_fiscal: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    data_hora: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    forma_pagamento: Mapped[Optional[str]] = mapped_column(String(20))
    valor_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), default=0)

    # Relacionamentos
    filial = relationship("Filial", back_populates="vendas")
    vendedor = relationship("Vendedor", back_populates="vendas")
    cliente = relationship("Cliente", back_populates="vendas")
    itens: Mapped[List["ItemVenda"]] = relationship(
        back_populates="venda", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Venda(id={self.id_venda}, cupom={self.cupom_fiscal})>"


class ItemVenda(Base):
    __tablename__ = "item_venda"

    id_item_venda: Mapped[int] = mapped_column(primary_key=True)
    id_venda: Mapped[int] = mapped_column(
        ForeignKey("venda.id_venda"), nullable=False
    )
    id_produto: Mapped[int] = mapped_column(
        ForeignKey("produto.id_produto"), nullable=False
    )
    # FK para prescricao mantida como coluna simples (tabela não mapeada neste CRUD)
    id_prescricao: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quantidade: Mapped[int] = mapped_column(Integer, default=0)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    desconto: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    valor_total: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        Computed(
            "(quantidade * preco_unitario)"
            " - ((quantidade * preco_unitario) * desconto)",
            persisted=True,
        ),
    )

    # Relacionamentos
    venda = relationship("Venda", back_populates="itens")
    produto = relationship("Produto")

    def __repr__(self) -> str:
        return f"<ItemVenda(id={self.id_item_venda}, venda={self.id_venda})>"
