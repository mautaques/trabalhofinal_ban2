"""Modelo ORM para a tabela *filial*."""

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Filial(Base):
    __tablename__ = "filial"

    id_filial: Mapped[int] = mapped_column(primary_key=True)
    codigo_filial: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    cnpj: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nome_fantasia: Mapped[str] = mapped_column(String(150), nullable=False)
    nome_gerente: Mapped[str] = mapped_column(String(150), nullable=False)
    telefone: Mapped[Optional[str]] = mapped_column(String(20))
    endereco: Mapped[Optional[str]] = mapped_column(Text)

    # Relacionamentos
    vendedores = relationship("Vendedor", back_populates="filial")
    vendas = relationship("Venda", back_populates="filial")

    def __repr__(self) -> str:
        return f"<Filial(id={self.id_filial}, codigo='{self.codigo_filial}')>"
