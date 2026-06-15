"""Serviço de negócio para a entidade Cliente."""

from sqlalchemy import or_

from database import get_session
from models.cliente import Cliente


class ClienteService:
    """CRUD e buscas para a tabela *cliente*."""

    @staticmethod
    def listar_todos():
        """Retorna todos os clientes ordenados por nome."""
        with get_session() as session:
            return session.query(Cliente).order_by(Cliente.nome).all()

    @staticmethod
    def buscar_por_id(id_cliente: int):
        """Retorna um cliente pelo ID."""
        with get_session() as session:
            return session.get(Cliente, id_cliente)

    @staticmethod
    def buscar(termo: str):
        """Busca clientes por nome, CPF ou e-mail."""
        with get_session() as session:
            return (
                session.query(Cliente)
                .filter(
                    or_(
                        Cliente.nome.ilike(f"%{termo}%"),
                        Cliente.cpf.ilike(f"%{termo}%"),
                        Cliente.mail.ilike(f"%{termo}%"),
                    )
                )
                .order_by(Cliente.nome)
                .all()
            )

    @staticmethod
    def criar(nome, cpf, telefone=None, mail=None, data_nascimento=None):
        """Cria um novo cliente. Valida campos obrigatórios e unicidade do CPF."""
        if not nome or not cpf:
            raise ValueError("Nome e CPF são obrigatórios.")

        with get_session() as session:
            existente = session.query(Cliente).filter_by(cpf=cpf).first()
            if existente:
                raise ValueError(f"CPF '{cpf}' já cadastrado.")

            cliente = Cliente(
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                mail=mail,
                data_nascimento=data_nascimento,
            )
            session.add(cliente)
            session.commit()
            session.refresh(cliente)
            return cliente

    @staticmethod
    def atualizar(id_cliente: int, **dados):
        """Atualiza os campos de um cliente existente."""
        with get_session() as session:
            cliente = session.get(Cliente, id_cliente)
            if not cliente:
                raise ValueError("Cliente não encontrado.")
            for campo, valor in dados.items():
                if hasattr(cliente, campo):
                    setattr(cliente, campo, valor)
            session.commit()
            session.refresh(cliente)
            return cliente

    @staticmethod
    def excluir(id_cliente: int):
        """Exclui um cliente pelo ID."""
        with get_session() as session:
            cliente = session.get(Cliente, id_cliente)
            if not cliente:
                raise ValueError("Cliente não encontrado.")
            session.delete(cliente)
            session.commit()
