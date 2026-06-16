"""Página de CRUD para Vendedores."""

from services.vendedor_service import VendedorService
from ui.pages.crud_page import CrudPage


class VendedorPage(CrudPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_page(
            title="Vendedores",
            columns=[
                {"key": "id_vendedor", "label": "ID"},
                {"key": "nome", "label": "Nome"},
                {"key": "cpf", "label": "CPF"},
                {"key": "matricula", "label": "Matrícula"},
                {"key": "cargo", "label": "Cargo"},
                {"key": "data_admissao", "label": "Admissão"},
                {"key": "comissao_percentual", "label": "Comissão (%)"},
            ],
            form_fields=[
                {"name": "nome", "label": "Nome", "type": "text",
                 "required": True, "max_length": 150},
                {"name": "cpf", "label": "CPF", "type": "text",
                 "required": True, "max_length": 12},
                {"name": "matricula", "label": "Matrícula", "type": "integer",
                 "required": True, "min": 1, "max": 999999},
                {"name": "cargo", "label": "Cargo", "type": "combobox",
                 "required": True,
                 "options": [
                     ("Atendente", "Atendente"),
                     ("Farmacêutico", "Farmacêutico"),
                 ]},
                {"name": "data_admissao", "label": "Data de Admissão",
                 "type": "date", "required": True},
                {"name": "comissao_percentual", "label": "Comissão (%)",
                 "type": "float", "decimals": 1, "min": 0.0, "max": 100.0},
            ],
            service=VendedorService,
            id_key="id_vendedor",
        )
