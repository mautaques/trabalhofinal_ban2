"""Camada de Dados — Modelos ORM (SQLAlchemy) mapeando as tabelas do banco."""

from models.cliente import Cliente
from models.produto import Produto
from models.vendedor import Vendedor
from models.fornecedor import Fornecedor
from models.filial import Filial
from models.venda import Venda, ItemVenda

__all__ = [
    "Cliente", "Produto", "Vendedor",
    "Fornecedor", "Filial", "Venda", "ItemVenda",
]
