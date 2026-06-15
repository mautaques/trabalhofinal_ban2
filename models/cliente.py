"""Modelo ORM para a tabela *cliente*."""

import datetime
from typing import Optional

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    cpf: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    telefone: Mapped[Optional[str]] = mapped_column(String(20))
    mail: Mapped[Optional[str]] = mapped_column(String(100))
    data_nascimento: Mapped[Optional[datetime.date]] = mapped_column(Date)

    # Relacionamentos
    vendas = relationship("Venda", back_populates="cliente")

    def __repr__(self) -> str:
        return f"<Cliente(id={self.id_cliente}, nome='{self.nome}')>"
