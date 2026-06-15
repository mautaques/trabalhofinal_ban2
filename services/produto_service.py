"""Serviço de negócio para a entidade Produto."""

from sqlalchemy import or_

from database import get_session
from models.produto import Produto


class ProdutoService:
    """CRUD e buscas para a tabela *produto*."""

    @staticmethod
    def listar_todos():
        """Retorna todos os produtos ordenados por nome."""
        with get_session() as session:
            return session.query(Produto).order_by(Produto.nome_produto).all()

    @staticmethod
    def buscar_por_id(id_produto: int):
        """Retorna um produto pelo ID."""
        with get_session() as session:
            return session.get(Produto, id_produto)

    @staticmethod
    def buscar(termo: str):
        """Busca produtos por nome, fabricante, código de barras ou categoria."""
        with get_session() as session:
            return (
                session.query(Produto)
                .filter(
                    or_(
                        Produto.nome_produto.ilike(f"%{termo}%"),
                        Produto.fabricante.ilike(f"%{termo}%"),
                        Produto.categoria.ilike(f"%{termo}%"),
                        Produto.codigo_de_barras.cast(str).ilike(f"%{termo}%"),
                    )
                )
                .order_by(Produto.nome_produto)
                .all()
            )

    @staticmethod
    def criar(
        codigo_de_barras,
        nome_produto,
        categoria,
        fabricante,
        principio_ativo=None,
        preco_custo=None,
        preco_venda=None,
        descricao=None,
    ):
        """Cria um novo produto. Valida campos obrigatórios e unicidade do código."""
        if not nome_produto or not fabricante:
            raise ValueError("Nome do produto e fabricante são obrigatórios.")
        if not codigo_de_barras:
            raise ValueError("Código de barras é obrigatório.")

        with get_session() as session:
            existente = (
                session.query(Produto)
                .filter_by(codigo_de_barras=int(codigo_de_barras))
                .first()
            )
            if existente:
                raise ValueError(
                    f"Código de barras '{codigo_de_barras}' já cadastrado."
                )

            produto = Produto(
                codigo_de_barras=int(codigo_de_barras),
                nome_produto=nome_produto,
                categoria=categoria,
                fabricante=fabricante,
                principio_ativo=principio_ativo,
                preco_custo=preco_custo,
                preco_venda=preco_venda,
                descricao=descricao,
            )
            session.add(produto)
            session.commit()
            session.refresh(produto)
            return produto

    @staticmethod
    def atualizar(id_produto: int, **dados):
        """Atualiza os campos de um produto existente."""
        with get_session() as session:
            produto = session.get(Produto, id_produto)
            if not produto:
                raise ValueError("Produto não encontrado.")
            # Não permitir alterar margem_lucro (coluna computada)
            dados.pop("margem_lucro", None)
            for campo, valor in dados.items():
                if hasattr(produto, campo):
                    setattr(produto, campo, valor)
            session.commit()
            session.refresh(produto)
            return produto

    @staticmethod
    def excluir(id_produto: int):
        """Exclui um produto pelo ID."""
        with get_session() as session:
            produto = session.get(Produto, id_produto)
            if not produto:
                raise ValueError("Produto não encontrado.")
            session.delete(produto)
            session.commit()
