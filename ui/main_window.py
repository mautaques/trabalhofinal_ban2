"""Janela principal do sistema — barra lateral de navegação + páginas."""

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from ui.pages.cliente_page import ClientePage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.filial_page import FilialPage
from ui.pages.fornecedor_page import FornecedorPage
from ui.pages.produto_page import ProdutoPage
from ui.pages.venda_page import VendaPage
from ui.pages.vendedor_page import VendedorPage


class MainWindow(QMainWindow):
    """Janela raiz com sidebar de navegação e QStackedWidget de páginas."""

    _PAGES = [
        ("📊  Dashboard", DashboardPage),
        ("👤  Clientes", ClientePage),
        ("📦  Produtos", ProdutoPage),
        ("🏷️  Vendedores", VendedorPage),
        ("🏢  Fornecedores", FornecedorPage),
        ("🏪  Filiais", FilialPage),
        ("🛒  Vendas", VendaPage),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gerência de Farmácia")
        self.setMinimumSize(1100, 650)
        self._setup_ui()
        self._check_connection()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────────────────
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setFont(QFont("", 11))
        self.sidebar.setSpacing(2)

        for label, _cls in self._PAGES:
            item = QListWidgetItem(label)
            item.setSizeHint(QSize(0, 40))
            self.sidebar.addItem(item)

        self.sidebar.currentRowChanged.connect(self._on_page_changed)
        main_layout.addWidget(self.sidebar)

        # ── Stack de páginas ─────────────────────────────────────────────
        self.stack = QStackedWidget()
        for _label, page_cls in self._PAGES:
            self.stack.addWidget(page_cls())
        main_layout.addWidget(self.stack)

        # Seleciona Dashboard por padrão
        self.sidebar.setCurrentRow(0)

    def _on_page_changed(self, index: int):
        self.stack.setCurrentIndex(index)
        page = self.stack.currentWidget()
        if hasattr(page, "load_data"):
            page.load_data()

    def _check_connection(self):
        from database import test_connection

        if test_connection():
            self.statusBar().showMessage("✓ Conectado ao PostgreSQL")
        else:
            self.statusBar().showMessage("✗ Falha na conexão com o PostgreSQL")
