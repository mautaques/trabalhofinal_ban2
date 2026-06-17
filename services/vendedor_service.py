"""Serviço de negócio para a entidade Vendedor."""

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from database import get_session
from models.vendedor import Vendedor


class VendedorService:
    """CRUD e buscas para a tabela *vendedor*."""

    @staticmethod
    def listar_todos():
        """Retorna todos os vendedores (com a filial) ordenados por nome."""
        with get_session() as session:
            return (
                session.query(Vendedor)
                .options(joinedload(Vendedor.filial))
                .order_by(Vendedor.nome)
                .all()
            )

    @staticmethod
    def buscar_por_id(id_vendedor: int):
        """Retorna um vendedor pelo ID."""
        with get_session() as session:
            return session.get(Vendedor, id_vendedor)

    @staticmethod
    def listar_por_filial(id_filial: int):
        """Retorna os vendedores de uma filial, ordenados por nome."""
        with get_session() as session:
            return (
                session.query(Vendedor)
                .filter_by(id_filial=id_filial)
                .order_by(Vendedor.nome)
                .all()
            )

    @staticmethod
    def buscar(termo: str):
        """Busca vendedores por nome, CPF ou cargo."""
        with get_session() as session:
            return (
                session.query(Vendedor)
                .options(joinedload(Vendedor.filial))
                .filter(
                    or_(
                        Vendedor.nome.ilike(f"%{termo}%"),
                        Vendedor.cpf.ilike(f"%{termo}%"),
                        Vendedor.cargo.ilike(f"%{termo}%"),
                    )
                )
                .order_by(Vendedor.nome)
                .all()
            )

    @staticmethod
    def criar(
        nome,
        cpf,
        matricula,
        cargo,
        data_admissao,
        id_filial,
        comissao_percentual=None,
    ):
        """Cria um novo vendedor. Valida unicidade de CPF e matrícula."""
        if not nome or not cpf or not cargo:
            raise ValueError("Nome, CPF e cargo são obrigatórios.")
        if not matricula:
            raise ValueError("Matrícula é obrigatória.")
        if not data_admissao:
            raise ValueError("Data de admissão é obrigatória.")
        if not id_filial:
            raise ValueError("Filial é obrigatória.")

        with get_session() as session:
            if session.query(Vendedor).filter_by(cpf=cpf).first():
                raise ValueError(f"CPF '{cpf}' já cadastrado.")
            if session.query(Vendedor).filter_by(matricula=matricula).first():
                raise ValueError(f"Matrícula '{matricula}' já cadastrada.")

            vendedor = Vendedor(
                nome=nome,
                cpf=cpf,
                matricula=int(matricula),
                cargo=cargo,
                data_admissao=data_admissao,
                comissao_percentual=comissao_percentual,
                id_filial=id_filial,
            )
            session.add(vendedor)
            session.commit()
            session.refresh(vendedor)
            return vendedor

    @staticmethod
    def atualizar(id_vendedor: int, **dados):
        """Atualiza os campos de um vendedor existente."""
        with get_session() as session:
            vendedor = session.get(Vendedor, id_vendedor)
            if not vendedor:
                raise ValueError("Vendedor não encontrado.")
            for campo, valor in dados.items():
                if hasattr(vendedor, campo):
                    setattr(vendedor, campo, valor)
            session.commit()
            session.refresh(vendedor)
            return vendedor

    @staticmethod
    def excluir(id_vendedor: int):
        """Exclui um vendedor pelo ID."""
        with get_session() as session:
            vendedor = session.get(Vendedor, id_vendedor)
            if not vendedor:
                raise ValueError("Vendedor não encontrado.")
            session.delete(vendedor)
            session.commit()
