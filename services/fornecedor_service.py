"""Serviço de negócio para a entidade Fornecedor."""

from sqlalchemy import or_

from database import get_session
from models.fornecedor import Fornecedor


class FornecedorService:
    """CRUD e buscas para a tabela *fornecedor*."""

    @staticmethod
    def listar_todos():
        """Retorna todos os fornecedores ordenados por nome fantasia."""
        with get_session() as session:
            return (
                session.query(Fornecedor)
                .order_by(Fornecedor.nome_fantasia)
                .all()
            )

    @staticmethod
    def buscar_por_id(id_fornecedor: int):
        """Retorna um fornecedor pelo ID."""
        with get_session() as session:
            return session.get(Fornecedor, id_fornecedor)

    @staticmethod
    def buscar(termo: str):
        """Busca fornecedores por nome fantasia, razão social ou CNPJ."""
        with get_session() as session:
            return (
                session.query(Fornecedor)
                .filter(
                    or_(
                        Fornecedor.nome_fantasia.ilike(f"%{termo}%"),
                        Fornecedor.razao_social.ilike(f"%{termo}%"),
                        Fornecedor.cnpj.ilike(f"%{termo}%"),
                    )
                )
                .order_by(Fornecedor.nome_fantasia)
                .all()
            )

    @staticmethod
    def criar(
        cnpj,
        razao_social,
        nome_fantasia,
        mail=None,
        telefone=None,
        condicoes_pagamento=None,
        endereco=None,
    ):
        """Cria um novo fornecedor. Valida unicidade de CNPJ e razão social."""
        if not cnpj or not razao_social or not nome_fantasia:
            raise ValueError("CNPJ, razão social e nome fantasia são obrigatórios.")

        with get_session() as session:
            if session.query(Fornecedor).filter_by(cnpj=cnpj).first():
                raise ValueError(f"CNPJ '{cnpj}' já cadastrado.")
            if session.query(Fornecedor).filter_by(razao_social=razao_social).first():
                raise ValueError(f"Razão social '{razao_social}' já cadastrada.")

            fornecedor = Fornecedor(
                cnpj=cnpj,
                razao_social=razao_social,
                nome_fantasia=nome_fantasia,
                mail=mail,
                telefone=telefone,
                condicoes_pagamento=condicoes_pagamento,
                endereco=endereco,
            )
            session.add(fornecedor)
            session.commit()
            session.refresh(fornecedor)
            return fornecedor

    @staticmethod
    def atualizar(id_fornecedor: int, **dados):
        """Atualiza os campos de um fornecedor existente."""
        with get_session() as session:
            fornecedor = session.get(Fornecedor, id_fornecedor)
            if not fornecedor:
                raise ValueError("Fornecedor não encontrado.")
            for campo, valor in dados.items():
                if hasattr(fornecedor, campo):
                    setattr(fornecedor, campo, valor)
            session.commit()
            session.refresh(fornecedor)
            return fornecedor

    @staticmethod
    def excluir(id_fornecedor: int):
        """Exclui um fornecedor pelo ID."""
        with get_session() as session:
            fornecedor = session.get(Fornecedor, id_fornecedor)
            if not fornecedor:
                raise ValueError("Fornecedor não encontrado.")
            session.delete(fornecedor)
            session.commit()
