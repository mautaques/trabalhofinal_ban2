"""Modelo ORM para a tabela *vendedor*."""

import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Vendedor(Base):
    __tablename__ = "vendedor"

    id_vendedor: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    cpf: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    matricula: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    cargo: Mapped[str] = mapped_column(String(20), nullable=False)
    data_admissao: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    comissao_percentual: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1))

    # Relacionamentos
    vendas = relationship("Venda", back_populates="vendedor")

    def __repr__(self) -> str:
        return f"<Vendedor(id={self.id_vendedor}, nome='{self.nome}')>"
