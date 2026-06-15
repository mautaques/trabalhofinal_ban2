"""Serviço de negócio para a entidade Filial."""

from sqlalchemy import or_

from database import get_session
from models.filial import Filial


class FilialService:
    """CRUD e buscas para a tabela *filial*."""

    @staticmethod
    def listar_todos():
        """Retorna todas as filiais ordenadas por código."""
        with get_session() as session:
            return session.query(Filial).order_by(Filial.codigo_filial).all()

    @staticmethod
    def buscar_por_id(id_filial: int):
        """Retorna uma filial pelo ID."""
        with get_session() as session:
            return session.get(Filial, id_filial)

    @staticmethod
    def buscar(termo: str):
        """Busca filiais por nome fantasia, código ou gerente."""
        with get_session() as session:
            return (
                session.query(Filial)
                .filter(
                    or_(
                        Filial.nome_fantasia.ilike(f"%{termo}%"),
                        Filial.codigo_filial.ilike(f"%{termo}%"),
                        Filial.nome_gerente.ilike(f"%{termo}%"),
                    )
                )
                .order_by(Filial.codigo_filial)
                .all()
            )

    @staticmethod
    def criar(
        codigo_filial,
        cnpj,
        nome_fantasia,
        nome_gerente,
        telefone=None,
        endereco=None,
    ):
        """Cria uma nova filial. Valida unicidade de código e CNPJ."""
        if not codigo_filial or not cnpj or not nome_fantasia or not nome_gerente:
            raise ValueError(
                "Código, CNPJ, nome fantasia e gerente são obrigatórios."
            )

        with get_session() as session:
            if session.query(Filial).filter_by(codigo_filial=codigo_filial).first():
                raise ValueError(f"Código '{codigo_filial}' já cadastrado.")
            if session.query(Filial).filter_by(cnpj=cnpj).first():
                raise ValueError(f"CNPJ '{cnpj}' já cadastrado.")

            filial = Filial(
                codigo_filial=codigo_filial,
                cnpj=cnpj,
                nome_fantasia=nome_fantasia,
                nome_gerente=nome_gerente,
                telefone=telefone,
                endereco=endereco,
            )
            session.add(filial)
            session.commit()
            session.refresh(filial)
            return filial

    @staticmethod
    def atualizar(id_filial: int, **dados):
        """Atualiza os campos de uma filial existente."""
        with get_session() as session:
            filial = session.get(Filial, id_filial)
            if not filial:
                raise ValueError("Filial não encontrada.")
            for campo, valor in dados.items():
                if hasattr(filial, campo):
                    setattr(filial, campo, valor)
            session.commit()
            session.refresh(filial)
            return filial

    @staticmethod
    def excluir(id_filial: int):
        """Exclui uma filial pelo ID."""
        with get_session() as session:
            filial = session.get(Filial, id_filial)
            if not filial:
                raise ValueError("Filial não encontrada.")
            session.delete(filial)
            session.commit()
