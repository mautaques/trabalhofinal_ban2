"""Modelo ORM para a tabela *produto*."""

from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Computed, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Produto(Base):
    __tablename__ = "produto"

    id_produto: Mapped[int] = mapped_column(primary_key=True)
    codigo_de_barras: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    nome_produto: Mapped[str] = mapped_column(String(150), nullable=False)
    categoria: Mapped[Optional[str]] = mapped_column(String(100))
    fabricante: Mapped[str] = mapped_column(String(150), nullable=False)
    principio_ativo: Mapped[Optional[str]] = mapped_column(String(50))
    preco_custo: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    preco_venda: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    margem_lucro: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        Computed("preco_venda - preco_custo", persisted=True),
    )
    descricao: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<Produto(id={self.id_produto}, nome='{self.nome_produto}')>"
