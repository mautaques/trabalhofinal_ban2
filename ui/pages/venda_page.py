"""Página de Vendas — master-detail (Venda ↔ Itens da Venda)."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.cliente_service import ClienteService
from services.filial_service import FilialService
from services.produto_service import ProdutoService
from services.venda_service import VendaService
from services.vendedor_service import VendedorService


class VendaPage(QWidget):
    """Painel master-detail: lista de vendas + itens da venda selecionada."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._vendas: list = []
        self._itens: list = []
        self._selected_venda = None
        self._setup_ui()
        self.load_data()

    # ── UI ───────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Vendas")
        title.setFont(QFont("", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Barra de ferramentas
        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por cupom fiscal ou cliente…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search)
        toolbar.addWidget(self.search_input, stretch=1)

        for text, slot in [
            ("Nova Venda", self._on_nova_venda),
            ("Excluir Venda", self._on_excluir_venda),
            ("Atualizar", self.load_data),
        ]:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            toolbar.addWidget(btn)

        layout.addLayout(toolbar)

        # Splitter vertical: vendas em cima, itens embaixo
        splitter = QSplitter(Qt.Orientation.Vertical)

        # ── Tabela de Vendas ─────────────────────────────────────────────
        self.vendas_table = self._make_table(
            ["ID", "Cupom Fiscal", "Filial", "Vendedor", "Cliente",
             "Data/Hora", "Forma Pgto", "Valor Total (R$)"]
        )
        self.vendas_table.selectionModel().selectionChanged.connect(
            self._on_venda_selected
        )
        splitter.addWidget(self.vendas_table)

        # ── Painel de Itens ──────────────────────────────────────────────
        items_panel = QWidget()
        items_layout = QVBoxLayout(items_panel)
        items_layout.setContentsMargins(0, 8, 0, 0)

        items_header = QHBoxLayout()
        self.items_title = QLabel("Itens da Venda")
        self.items_title.setFont(QFont("", 12, QFont.Weight.Bold))
        items_header.addWidget(self.items_title)
        items_header.addStretch()

        btn_add = QPushButton("Adicionar Item")
        btn_add.clicked.connect(self._on_add_item)
        items_header.addWidget(btn_add)

        btn_rm = QPushButton("Remover Item")
        btn_rm.clicked.connect(self._on_remove_item)
        items_header.addWidget(btn_rm)

        items_layout.addLayout(items_header)

        self.items_table = self._make_table(
            ["ID", "Produto", "Quantidade", "Preço Unit. (R$)",
             "Desconto", "Valor Total (R$)"]
        )
        items_layout.addWidget(self.items_table)

        splitter.addWidget(items_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

    @staticmethod
    def _make_table(headers: list[str]) -> QTableWidget:
        t = QTableWidget()
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.setAlternatingRowColors(True)
        t.horizontalHeader().setStretchLastSection(True)
        t.verticalHeader().setVisible(False)
        return t

    # ── Dados ────────────────────────────────────────────────────────────

    def load_data(self):
        """Carrega todas as vendas na tabela."""
        try:
            self._vendas = VendaService.listar_todos()
            self._populate_vendas()
        except Exception as exc:
            QMessageBox.critical(self, "Erro", str(exc))

    def _on_search(self, text: str):
        try:
            if text.strip():
                self._vendas = VendaService.buscar(text)
            else:
                self._vendas = VendaService.listar_todos()
            self._populate_vendas()
        except Exception as exc:
            QMessageBox.critical(self, "Erro", str(exc))

    def _populate_vendas(self):
        self.vendas_table.setRowCount(len(self._vendas))
        for row, v in enumerate(self._vendas):
            self.vendas_table.setItem(row, 0, QTableWidgetItem(str(v.id_venda)))
            self.vendas_table.setItem(row, 1, QTableWidgetItem(str(v.cupom_fiscal)))
            self.vendas_table.setItem(
                row, 2,
                QTableWidgetItem(v.filial.nome_fantasia if v.filial else ""),
            )
            self.vendas_table.setItem(
                row, 3,
                QTableWidgetItem(v.vendedor.nome if v.vendedor else ""),
            )
            self.vendas_table.setItem(
                row, 4,
                QTableWidgetItem(v.cliente.nome if v.cliente else ""),
            )
            data_str = v.data_hora.strftime("%d/%m/%Y %H:%M") if v.data_hora else ""
            self.vendas_table.setItem(row, 5, QTableWidgetItem(data_str))
            self.vendas_table.setItem(
                row, 6, QTableWidgetItem(v.forma_pagamento or "")
            )
            valor = f"{v.valor_total:.2f}" if v.valor_total else "0.00"
            self.vendas_table.setItem(row, 7, QTableWidgetItem(valor))
        self.vendas_table.resizeColumnsToContents()
        self.items_table.setRowCount(0)
        self._selected_venda = None
        self.items_title.setText("Itens da Venda")

    def _on_venda_selected(self):
        rows = self.vendas_table.selectionModel().selectedRows()
        if not rows:
            return
        venda = self._vendas[rows[0].row()]
        self._selected_venda = venda
        self.items_title.setText(f"Itens da Venda #{venda.cupom_fiscal}")
        try:
            self._itens = VendaService.buscar_itens(venda.id_venda)
            self._populate_itens()
        except Exception as exc:
            QMessageBox.critical(self, "Erro", str(exc))

    def _populate_itens(self):
        self.items_table.setRowCount(len(self._itens))
        for row, it in enumerate(self._itens):
            self.items_table.setItem(
                row, 0, QTableWidgetItem(str(it.id_item_venda))
            )
            nome_prod = it.produto.nome_produto if it.produto else str(it.id_produto)
            self.items_table.setItem(row, 1, QTableWidgetItem(nome_prod))
            self.items_table.setItem(
                row, 2, QTableWidgetItem(str(it.quantidade))
            )
            self.items_table.setItem(
                row, 3, QTableWidgetItem(f"{it.preco_unitario:.2f}")
            )
            desc = f"{float(it.desconto) * 100:.0f}%" if it.desconto else "—"
            self.items_table.setItem(row, 4, QTableWidgetItem(desc))
            vtotal = f"{it.valor_total:.2f}" if it.valor_total else "—"
            self.items_table.setItem(row, 5, QTableWidgetItem(vtotal))
        self.items_table.resizeColumnsToContents()

    # ── CRUD Venda ───────────────────────────────────────────────────────

    def _on_nova_venda(self):
        dlg = _NovaVendaDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            vals = dlg.get_values()
            try:
                VendaService.criar(**vals)
                self.load_data()
            except Exception as exc:
                QMessageBox.critical(self, "Erro ao Criar Venda", str(exc))

    def _on_excluir_venda(self):
        if not self._selected_venda:
            QMessageBox.warning(self, "Aviso", "Selecione uma venda.")
            return
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Excluir venda #{self._selected_venda.cupom_fiscal} e todos seus itens?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                VendaService.excluir(self._selected_venda.id_venda)
                self.load_data()
            except Exception as exc:
                QMessageBox.critical(self, "Erro ao Excluir", str(exc))

    # ── CRUD Itens ───────────────────────────────────────────────────────

    def _on_add_item(self):
        if not self._selected_venda:
            QMessageBox.warning(self, "Aviso", "Selecione uma venda primeiro.")
            return
        dlg = _NovoItemDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            vals = dlg.get_values()
            try:
                VendaService.adicionar_item(
                    self._selected_venda.id_venda, **vals
                )
                self._on_venda_selected()  # recarrega itens
                self.load_data()           # recarrega total da venda
                # Re-seleciona a venda
                for i, v in enumerate(self._vendas):
                    if v.id_venda == self._selected_venda.id_venda:
                        self.vendas_table.selectRow(i)
                        break
            except Exception as exc:
                QMessageBox.critical(self, "Erro ao Adicionar Item", str(exc))

    def _on_remove_item(self):
        if not self._selected_venda:
            QMessageBox.warning(self, "Aviso", "Selecione uma venda primeiro.")
            return
        rows = self.items_table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Aviso", "Selecione um item para remover.")
            return
        item = self._itens[rows[0].row()]
        reply = QMessageBox.question(
            self, "Confirmar Remoção",
            "Remover este item da venda?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                VendaService.remover_item(item.id_item_venda)
                self._on_venda_selected()
                self.load_data()
                for i, v in enumerate(self._vendas):
                    if v.id_venda == self._selected_venda.id_venda:
                        self.vendas_table.selectRow(i)
                        break
            except Exception as exc:
                QMessageBox.critical(self, "Erro ao Remover Item", str(exc))


# ── Diálogos auxiliares ──────────────────────────────────────────────────


class _NovaVendaDialog(QDialog):
    """Formulário para criação de uma nova venda."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Venda")
        self.setMinimumWidth(420)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        # Filial
        self.cmb_filial = QComboBox()
        try:
            for f in FilialService.listar_todos():
                self.cmb_filial.addItem(
                    f"{f.codigo_filial} — {f.nome_fantasia}", f.id_filial
                )
        except Exception:
            pass
        layout.addRow("Filial *:", self.cmb_filial)

        # Vendedor
        self.cmb_vendedor = QComboBox()
        try:
            for v in VendedorService.listar_todos():
                self.cmb_vendedor.addItem(
                    f"{v.matricula} — {v.nome}", v.id_vendedor
                )
        except Exception:
            pass
        layout.addRow("Vendedor *:", self.cmb_vendedor)

        # Cliente
        self.cmb_cliente = QComboBox()
        try:
            for c in ClienteService.listar_todos():
                self.cmb_cliente.addItem(f"{c.nome} ({c.cpf})", c.id_cliente)
        except Exception:
            pass
        layout.addRow("Cliente *:", self.cmb_cliente)

        # Cupom fiscal
        self.spn_cupom = QSpinBox()
        self.spn_cupom.setRange(1, 999_999_999)
        layout.addRow("Cupom Fiscal *:", self.spn_cupom)

        # Forma de pagamento
        self.cmb_pgto = QComboBox()
        for val, label in [
            ("Pix", "Pix"),
            ("Cartão de Crédito", "Cartão de Crédito"),
            ("Cartão de Débito", "Cartão de Débito"),
        ]:
            self.cmb_pgto.addItem(label, val)
        layout.addRow("Forma de Pagamento:", self.cmb_pgto)

        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_values(self) -> dict:
        return {
            "id_filial": self.cmb_filial.currentData(),
            "id_vendedor": self.cmb_vendedor.currentData(),
            "id_cliente": self.cmb_cliente.currentData(),
            "cupom_fiscal": self.spn_cupom.value(),
            "forma_pagamento": self.cmb_pgto.currentData(),
        }


class _NovoItemDialog(QDialog):
    """Formulário para adicionar um item a uma venda existente."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Item à Venda")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        # Produto
        self.cmb_produto = QComboBox()
        try:
            for p in ProdutoService.listar_todos():
                self.cmb_produto.addItem(
                    f"{p.nome_produto} (R$ {p.preco_venda})", p.id_produto
                )
        except Exception:
            pass
        layout.addRow("Produto *:", self.cmb_produto)

        # Quantidade
        self.spn_qtd = QSpinBox()
        self.spn_qtd.setRange(1, 9999)
        self.spn_qtd.setValue(1)
        layout.addRow("Quantidade *:", self.spn_qtd)

        # Preço unitário
        self.spn_preco = QDoubleSpinBox()
        self.spn_preco.setRange(0.01, 99999.99)
        self.spn_preco.setDecimals(2)
        layout.addRow("Preço Unitário (R$) *:", self.spn_preco)

        # Desconto (fração: 0.10 = 10%)
        self.spn_desconto = QDoubleSpinBox()
        self.spn_desconto.setRange(0.0, 1.0)
        self.spn_desconto.setDecimals(2)
        self.spn_desconto.setSingleStep(0.05)
        self.spn_desconto.setToolTip("Fração: 0.10 = 10% de desconto")
        layout.addRow("Desconto (0 a 1):", self.spn_desconto)

        # Atualiza preço quando produto muda
        self.cmb_produto.currentIndexChanged.connect(self._on_produto_changed)
        self._on_produto_changed()

        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _on_produto_changed(self):
        """Preenche o preço unitário com o preço de venda do produto."""
        try:
            id_prod = self.cmb_produto.currentData()
            if id_prod:
                prod = ProdutoService.buscar_por_id(id_prod)
                if prod and prod.preco_venda:
                    self.spn_preco.setValue(float(prod.preco_venda))
        except Exception:
            pass

    def get_values(self) -> dict:
        desconto = self.spn_desconto.value()
        return {
            "id_produto": self.cmb_produto.currentData(),
            "quantidade": self.spn_qtd.value(),
            "preco_unitario": self.spn_preco.value(),
            "desconto": desconto if desconto > 0 else None,
        }
