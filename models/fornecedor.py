"""Modelo ORM para a tabela *fornecedor*."""

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Fornecedor(Base):
    __tablename__ = "fornecedor"

    id_fornecedor: Mapped[int] = mapped_column(primary_key=True)
    cnpj: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    razao_social: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    nome_fantasia: Mapped[str] = mapped_column(String(150), nullable=False)
    mail: Mapped[Optional[str]] = mapped_column(String(100))
    telefone: Mapped[Optional[str]] = mapped_column(String(20))
    condicoes_pagamento: Mapped[Optional[str]] = mapped_column(String(50))
    endereco: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<Fornecedor(id={self.id_fornecedor}, nome='{self.nome_fantasia}')>"
